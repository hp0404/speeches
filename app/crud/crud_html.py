import typing

from fastapi import HTTPException
from sqlmodel import Session, SQLModel

from app.helpers import calculate_stats, create_pipeline
from app.helpers.transform import InvalidHTML, Transformer, create_nlp
from app.models import (
    Exports,
    ExtractedFeatures,
    Metadata,
    Sentences,
    TextStatistics,
    Themes,
)

nlp = create_nlp()
KeyPhraseMatcher = create_pipeline()


class CRUDHTHML:
    def __init__(self, backend: Transformer):
        self.backend = backend

    def is_present(self, db: Session) -> bool:
        id_check = db.get(Metadata, self.backend.document_id)
        return bool(id_check)

    def create(self, db: Session) -> None:
        if self.is_present(db):
            raise HTTPException(
                status_code=409, detail="This file has already been added"
            )
        model = self.backend.as_model()
        metadata = Metadata(
            id=model.id, title=model.title, date=model.date, url=model.url
        )
        metadata.raw_export = Exports(
            id=model.id, html_contents=self.backend.html_contents
        )
        if model.themes is not None:
            for value in model.themes:
                theme = Themes(
                    document_id=model.id, category=value.category, theme=value.theme
                )
                metadata.themes.append(theme)
        for value in model.sentences:
            sentence = Sentences(
                document_id=value.document_id,
                paragraph_id=value.paragraph_id,
                sentence_id=value.sentence_id,
                speaker=value.speaker,
                text=value.text,
                text_lemmatized=value.text_lemmatized,
            )
            ts = calculate_stats(sentence.text)
            if ts is not None:
                sentence.textstats = TextStatistics(
                    sentence_id=sentence.id, statistics=ts
                )
            data_tuple = [(sentence.text, "discard")]
            for noun_phrase in KeyPhraseMatcher.yield_key_phrases(data_tuple):
                phrase = ExtractedFeatures(
                    sentence_id=sentence.id,
                    entity_type=noun_phrase["entity_type"],
                    label=noun_phrase["label"],
                    match=noun_phrase["match"],
                    match_processed=noun_phrase["match_processed"],
                    span_location=noun_phrase["span_location"],
                )
                sentence.phrases.append(phrase)
            metadata.sentences.append(sentence)
        db.add(metadata)
        db.commit()

def create_html_processor(html_contents: bytes) -> CRUDHTHML:
    try:
        backend = Transformer(html_contents=html_contents, nlp=nlp)
    except InvalidHTML:
        raise HTTPException(status_code=422, detail="Unprocessable entity")
    return CRUDHTHML(backend=backend)
