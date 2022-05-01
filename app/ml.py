# -*- coding: utf-8 -*-
import json
from pathlib import Path
from typing import Any, Dict, List, Union, Iterator, Tuple, NamedTuple

import spacy

Data = Dict[str, str]
Feature = Dict[str, Union[str, Tuple[int, int]]]


class Rule(NamedTuple):
    label: str
    pattern: List[List[Dict[str, Any]]]


def read_pattern(path: Path) -> List[Rule]:
    """Reads patterns JSON file."""
    with path.open("r", encoding="utf-8") as file_content:
        content = json.load(file_content)["patterns"]
    return [Rule(label=p["label"], pattern=p["pattern"]) for p in content]


class ML:
    """Extracts noun-phrases & named-entities."""

    def __init__(self, nlp: spacy.language.Language, patterns: Path) -> None:
        self.nlp = nlp
        self.patterns_location = patterns
        self.phrase_matcher = self.build_phrase_matcher()

    def build_phrase_matcher(self) -> spacy.matcher.Matcher:
        """Builds custom matcher."""
        matcher = spacy.matcher.Matcher(self.nlp.vocab)
        if self.patterns_location.is_dir():
            for patterns_file in self.patterns_location.rglob("*.json"):
                patterns = read_pattern(patterns_file)
                for pattern in patterns:
                    matcher.add(pattern.label, pattern.pattern)
        elif self.patterns_location.is_file():
            patterns = read_pattern(self.patterns_location)
            for pattern in patterns:
                matcher.add(pattern.label, pattern.pattern)
        else:
            raise ValueError(
                "patterns_location should either be a non-empty dir or a file."
            )
        return matcher

    def _stream_named_entities(
        self, doc: spacy.tokens.doc.Doc, uuid: str
    ) -> Iterator[Feature]:
        """Streams named entities."""
        for entity in doc.ents:
            yield {
                "document_id": uuid,
                "feature_type": "NE",
                "feature_label": entity.label_,
                "match": entity.text,
                "match_normalized": entity.lemma_,
                "location": (entity.start_char, entity.end_char),
            }

    def _stream_noun_phrases(
        self, doc: spacy.tokens.doc.Doc, uuid: str
    ) -> Iterator[Feature]:
        """Streams noun phrases."""
        for match_id, start, end in self.phrase_matcher(doc):
            span = doc[start:end]
            yield {
                "document_id": uuid,
                "feature_type": "NP",
                "feature_label": self.nlp.vocab[match_id].text,
                "match": span.text,
                "match_normalized": span.lemma_,
                "location": (span.start_char, span.end_char),
            }

    def stream(self, data: Data, batch_size: int = 25) -> Iterator[Feature]:
        for doc, uuid in self.nlp.pipe(data, as_tuples=True, batch_size=batch_size):  # type: ignore
            yield from self._stream_named_entities(doc, uuid)
            yield from self._stream_noun_phrases(doc, uuid)


def create_pipeline() -> ML:
    nlp = spacy.load("ru_core_news_sm")
    patterns = Path(__file__).resolve().parent.parent / "assets" / "patterns"
    return ML(nlp, patterns=patterns)


feature_extractor = create_pipeline()
