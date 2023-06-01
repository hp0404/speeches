# -*- coding: utf-8 -*-
from fastapi import HTTPException
from sqlmodel import Session

from app.helpers.ml import create_pipeline, nlp
from app.helpers.red_lines import RedLinesClassifier
from app.helpers.sentiment import SentimentScorer
from app.helpers.textstats import calculate_stats
from app.helpers.transform import InvalidHTML, Transformer
from app.models import (
    Embeddings,
    Exports,
    ExtractedFeatures,
    Metadata,
    RedLines,
    Sentences,
    Sentiment,
    TextStatistics,
    Themes,
)

KeyPhraseMatcher = create_pipeline()
classifier = RedLinesClassifier()
sentiment = SentimentScorer()


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
        for sent in model.sentences:
            sentence = Sentences(
                document_id=sent.document_id,
                paragraph_id=sent.paragraph_id,
                sentence_id=sent.sentence_id,
                speaker=sent.speaker,
                text=sent.text,
                text_lemmatized=sent.text_lemmatized,
            )
            ts = calculate_stats(sentence.text)
            if ts is not None:
                sentence.textstats = TextStatistics.from_orm(ts)

            prediction = classifier.store(sent.text)
            sentence.redlines = RedLines(
                sentence_id=sent.sentence_id,
                model_language=prediction.model_language,
                model_name=prediction.model_name,
                model_type=prediction.model_type,
                model_performance=prediction.model_performance,
                model_version=prediction.model_version,
                prediction=prediction.prediction,
            )

            vector = nlp(sent.text).vector.tolist()
            sentence.embeddings = Embeddings(
                sentence_id=sent.sentence_id,
                model_language=nlp.meta["lang"],
                model_name=nlp.meta["name"],
                vector=vector,
            )

            sentiment_prediction = sentiment.predict(sent.text)
            sentence.sentiments = Sentiment(
                sentence_id=sent.sentence_id,
                model_name=sentiment_prediction.model_name,
                tokenizer_name=sentiment_prediction.tokenizer_name,
                prediction=sentiment_prediction.prediction,
                prediction_label=sentiment_prediction.prediction_label,
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
        backend = Transformer(html_contents=html_contents, nlp_model=nlp)
    except InvalidHTML:
        raise HTTPException(status_code=422, detail="Unprocessable entity")
    return CRUDHTHML(backend=backend)
