# -*- coding: utf-8 -*-
"""This module contains ML-related utilities."""
import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, NamedTuple, Optional, Tuple, Union
from uuid import UUID

import spacy

DataTuple = List[Tuple[str, UUID]]
Feature = Dict[str, Union[str, UUID, List[int]]]


class Rule(NamedTuple):
    """Patterns structure."""

    label: str
    pattern: List[List[Dict[str, Any]]]


def read_pattern(path: Path) -> List[Rule]:
    """Reads patterns JSON file."""
    with path.open("r", encoding="utf-8") as file_content:
        content = json.load(file_content)["patterns"]
    return [Rule(label=p["label"], pattern=p["pattern"]) for p in content]


def force_path(s: Union[str, Path]) -> Path:
    """Casts input to Path."""
    if isinstance(s, Path):
        return s
    return Path(s).resolve()


class ML:
    """Base class that will handle ML-related utilities"""

    def __init__(
        self, nlp: spacy.language.Language, patterns: Union[str, Path]
    ) -> None:
        self.nlp = nlp
        self.patterns_location = force_path(patterns)
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

    def _stream_named_entities(  # pylint: disable=no-self-use
        self,
        doc: spacy.tokens.doc.Doc,  # pylint: disable=c-extension-no-member
        uuid: UUID,
    ) -> Iterator[Feature]:
        """Streams named entities."""
        for entity in doc.ents:
            yield {
                "document_id": uuid,
                "feature_type": "NE",
                "feature_label": entity.label_,
                "match": entity.text,
                "match_normalized": entity.lemma_,
                "location": [entity.start_char, entity.end_char],
            }

    def _stream_noun_phrases(
        self,
        doc: spacy.tokens.doc.Doc,  # pylint: disable=c-extension-no-member
        uuid: UUID,
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
                "location": [span.start_char, span.end_char],
            }

    def stream(self, data: DataTuple, batch: int = 25) -> Iterator[Feature]:
        """Streams extracted features."""
        for doc, uuid in self.nlp.pipe(data, as_tuples=True, batch_size=batch):
            yield from self._stream_named_entities(doc, uuid)
            yield from self._stream_noun_phrases(doc, uuid)


def create_pipeline(
    model: str = "ru_core_news_sm", patterns: Optional[Path] = None
) -> ML:
    """Initializes ML pipeline."""
    nlp = spacy.load(model)
    if patterns is None:
        patterns = Path(__file__).resolve().parent.parent / "assets" / "patterns"
    return ML(nlp, patterns=patterns)


feature_extractor = create_pipeline()
