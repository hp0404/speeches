# -*- coding: utf-8 -*-
import re
import typing

import spacy
from bs4 import BeautifulSoup

from app.schemas import Document, Sentence, Theme

RE_SPEAKER = re.compile(
    r"(^\w+[\s\.\-][А-ЯA-Z]\w+\:|^\w+[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w+\:|^\w+[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w+\:|^\w+[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w+\:|^\«.{2,50}\»\:|^.{2,40}\«.{2,40}\»\:|^.{4,40}\(.+?\)\:)",
    flags=re.IGNORECASE,
)


class InvalidHTML(ValueError):
    pass


class Transformer:
    def __init__(
        self, html_contents: bytes, nlp: typing.Optional[spacy.language.Language] = None
    ):
        self.nlp = nlp if nlp is not None else create_nlp()
        self.html_contents = html_contents
        self.soup = BeautifulSoup(html_contents, "html.parser")
        self.document_id = None
        self.title = None
        self.date = None
        self.url = None
        self.themes = None
        self.sentences = None
        # always running metadata first
        self._extract_metadata()

    def as_model(self) -> Document:
        if self.themes is None:
            try:
                self.themes = self._extract_themes()
            except InvalidHTML:
                self.themes = None
        themes = (
            [Theme(**theme) for theme in self.themes]
            if self.themes is not None
            else None
        )
        if self.sentences is None:
            self.sentences = self._extract_sentences()
        return Document(
            id=self.document_id,
            title=self.title,
            date=self.date,
            url=self.url,
            themes=themes,
            sentences=[Sentence(**sent) for sent in self.sentences],
        )

    def _extract_themes(self) -> typing.List[typing.Dict[str, str]]:
        data = []
        tags_block = self.soup.select_one(
            "div.read__bottommeta.hidden-copy > div > div.read__tags.masha-ignore"
        )
        if tags_block is None:
            raise InvalidHTML("Tags block is missing.")
        for tag in tags_block.find_all(class_="read__tagscol"):
            title = tag.h3.text.strip()
            for li in tag.select("li"):
                item = li.text.strip()
                data.append({"category": title, "theme": item.strip()})
        return data

    def _extract_metadata(self) -> None:
        meta = self.soup.select_one("div.read__top")
        if meta is None:
            raise InvalidHTML("The top part of the page is missing. Inspect the page.")

        url = self.soup.select_one("#material_link")
        if url is None:
            raise InvalidHTML("#material_link is not present. Inspect the page first.")

        self.document_id = int(url.text.split("/")[-1])
        self.title = meta.select_one("h1").text.replace("\xa0", " ")  # type: ignore
        self.date = meta.select_one("div.read__meta > time")["datetime"]  # type: ignore
        self.url = url.text
        return None

    def _extract_sentences(self) -> typing.List[typing.Dict[str, typing.Any]]:
        data = []
        meta_speaker: typing.Optional[str] = None
        paragraphs = self.soup.select(
            "div.entry-content.e-content.read__internal_content > p"
        )
        for paragraph_id, paragraph in enumerate(paragraphs, start=1):
            has_bold = paragraph.find("b")
            paragraph_speaker_matching = re.search(RE_SPEAKER, paragraph.text)
            try:
                paragraph_speaker = paragraph_speaker_matching.group()  # type: ignore
            except AttributeError:
                paragraph_speaker = None
            # if highlighted
            if paragraph_speaker: # and has_bold:
                meta_speaker = paragraph_speaker
            doc = self.nlp(paragraph.text)
            for sentence_id, sentence in enumerate(doc.sents, start=1):
                try:
                    sentence_speaker = re.search(RE_SPEAKER, sentence.text.strip()).group()  # type: ignore
                except AttributeError:
                    sentence_speaker = paragraph_speaker
                if sentence_speaker is None and meta_speaker is not None:
                    sentence_speaker = meta_speaker
                processed_text = self.clean_text(sentence.text)
                if processed_text:
                    data.append(
                        {
                            "document_id": self.document_id,
                            "paragraph_id": paragraph_id,
                            "sentence_id": sentence_id,
                            "text": processed_text,
                            "text_lemmatized": " ".join(
                                t.lemma_.lower()
                                for t in sentence
                                if t.is_alpha and not t.is_stop
                            ),
                            "speaker": sentence_speaker.strip(":")
                            if sentence_speaker is not None
                            else None,
                        }
                    )
        return data

    @staticmethod
    def clean_text(text: str) -> str:
        cleaned_text = text
        for pattern in (r"\*", r"\xa0", r"\n", r"^\w+\.\w+\:\s+", r"<…>"):
            cleaned_text = re.sub(pattern, " ", cleaned_text)
        return cleaned_text.strip()


def create_nlp(model: str = "ru_core_news_sm") -> spacy.language.Language:
    return spacy.load(model)
