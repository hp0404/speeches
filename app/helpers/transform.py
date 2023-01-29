# -*- coding: utf-8 -*-
import re
import typing

import spacy
from bs4 import BeautifulSoup

from app.helpers.ml import nlp
from app.schemas import Document, Sentence, Theme

RE_SPEAKER = re.compile(
    r"(^\w+[\s\.\-][А-ЯA-Z]\w+\:|^\w+[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w+\:|^\w+[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w+\:|^\w+[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w*[\s\.\-][А-ЯA-Z]\w+\:|^\«.{2,50}\»\:|^.{2,40}\«.{2,40}\»\:|^.{4,40}\(.+?\)\:)",
    flags=re.IGNORECASE,
)


class InvalidHTML(ValueError):
    pass


class Transformer:
    def __init__(
        self,
        html_contents: bytes,
        nlp_model: typing.Optional[spacy.language.Language] = None,
    ):
        self.nlp = nlp_model if nlp_model is not None else nlp
        self.html_contents = html_contents
        self.soup = BeautifulSoup(html_contents, "html.parser")
        self.document_id: typing.Optional[int] = None
        self.title = None
        self.date = None
        self.url: typing.Optional[str] = None
        self.themes: typing.Optional[typing.List[typing.Dict[str, str]]] = None
        self.sentences: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
        # always running metadata first
        self._extract_metadata()

    def as_model(self) -> Document:
        if self.themes is None:
            try:
                self.themes = self._extract_themes()
            except InvalidHTML:
                self.themes = None
        if self.sentences is None:
            self.sentences = self._extract_sentences()
        return Document(
            id=self.document_id,
            title=self.title,
            date=self.date,
            url=self.url,
            themes=(
                [Theme(**theme) for theme in self.themes]
                if self.themes is not None
                else None
            ),
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
        previous_speaker: typing.Optional[str] = None
        paragraphs = self.soup.select(
            "div.entry-content.e-content.read__internal_content > p"
        )
        for paragraph_id, paragraph in enumerate(paragraphs, start=1):
            paragraph_speaker: typing.Optional[str] = None
            m = re.search(RE_SPEAKER, paragraph.text)
            if m is not None:
                possible_speaker = m.group().strip()
                dot = re.search(r"\.", possible_speaker)
                if dot is not None:
                    paragraph_speaker = possible_speaker
                    previous_speaker = paragraph_speaker
            if paragraph_speaker is None and previous_speaker is not None:
                paragraph_speaker = previous_speaker
            doc = self.nlp(paragraph.text)
            for sentence_id, sentence in enumerate(doc.sents, start=1):
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
                            "speaker": paragraph_speaker.strip(":")
                            if paragraph_speaker is not None
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
