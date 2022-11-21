# -*- coding: utf-8 -*-
"""This module contains ML-related utilities."""
import json
import typing
from pathlib import Path

import spacy
from spacy.matcher import Matcher
from spacy.symbols import VERB, nsubj, nsubjpass
from spacy.tokens import Span

from app.helpers.treebank import is_vbg, is_vbn


class Rule(typing.NamedTuple):
    """Patterns structure."""

    label: str
    pattern: typing.List[typing.List[typing.Dict[str, typing.Any]]]


def read_pattern(path: Path) -> typing.List[Rule]:
    """Reads patterns JSON file."""
    with path.open("r", encoding="utf-8") as file_content:
        content = json.load(file_content)
    return [Rule(label=p["label"], pattern=p["pattern"]) for p in content]


def build_matcher(nlp: spacy.language.Language, patterns: Path) -> Matcher:
    """Builds custom matcher.
    Parameters
    ----------
    nlp: spacy.language.Language
        The matcher will operate on the vocabulary object (spacy's model vocab
        attribute)
    patterns: Path
        Path to a .json file with predefined POS patterns; it should follow
        this schema:
        [
            {
                "label": "ADJ-NOUN",
                "pattern": [
                    [{"POS": "ADJ"}, {"POS": "NOUN"}]
                ]
            },
            {
                "label": "ADJ-ADJ-NOUN",
                "pattern": [
                    [{"POS": "ADJ"}, {"POS": "ADJ"}, {"POS": "NOUN"}]
                ]
            }
        ]
    """
    matcher = Matcher(nlp.vocab)
    combinations = read_pattern(patterns)
    for combination in combinations:
        matcher.add(combination.label, combination.pattern)
    return matcher


class ML:
    """Key Noun Phrase matcher."""

    def __init__(
        self, nlp: spacy.language.Language, matcher: typing.Optional[Matcher] = None
    ):
        """Initializes TermsMatcher class.
        Parameters
        ----------
        nlp: spacy.language.Language
            spacy's model
        matcher: spacy.match.Matcher
            spacy's rule-based Matcher;
            defaults to our own implementation but could be replaced with a custom one
        """
        self.nlp = nlp
        self._default_patterns = (
            Path(__file__).resolve().parent / "assets" / "default_patterns.json"
        )
        self.matcher = (
            matcher
            if matcher is not None
            else build_matcher(nlp, self._default_patterns)
        )

    def yield_key_phrases(
        self,
        sentences: typing.List[typing.Tuple[str, str]],
        batch_size: int = 25,
        exclusive_search: bool = True,
    ) -> typing.Iterator[typing.Dict[str, typing.Any]]:
        """Yields key noun phrases found in sentences.
        Parameters
        ----------
        sentences: list[tuple[uuid, text]]
            list of pairs, each consisting of text and its identifier (so that
            we could 'place' exact phrase within some context (found by uuid);
            it must follow this structure: [("Some text", "uuid1"), ("Another sentence", "uuid2"), ...]
        batch_size: int
            the number of texts to buffer
        exclusive_search: bool
            whether to yield
              - phrases with nsubj being part of them (True) and
              - VERB-based phrases with finegrained VERB subtypes (True)
            to yield any phrases found within the nsubj's subtree (even without
            nsubj token being a part of the phrase) (False) and any VERB-based phrases
        Usage
        -----
        >>> from spacy.lang.ru.examples import sentences
        >>> nlp = spacy.load("ru_core_news_md")
        >>> terms = TermsMatcher(nlp=nlp)
        >>> transformed_sentences = [(sent, idx) for idx, sent in enumerate(sentences)]
        >>> for key_noun_phrase in terms.yield_key_phrases(transformed_sentences):
        ...     print(key_noun_phrase)
        ...
        Notes
        -----
        The idea behind _key_ noun phrase is that we only care about phrases
        that stem from the token which has nsubj dependency tag and whose
        head token has VERB pos tag (as it's (arguably) more important than other phrases).
        Thus, we limit the context -- from the full document to a limited
        subtree or even token's direct children -- within which we're going to
        match phrases according to our pos combinations.
        """
        for sentence, _ in self.nlp.pipe(
            sentences, as_tuples=True, batch_size=batch_size
        ):
            for possible_subject in sentence:
                if (
                    possible_subject.dep in [nsubj, nsubjpass]
                    and possible_subject.head.pos == VERB
                ):
                    subtree = sentence[
                        possible_subject.left_edge.i : possible_subject.right_edge.i + 1
                    ]
                    yield from self.match(
                        subtree,
                        possible_subject=possible_subject,
                        exclusive_search=exclusive_search,
                    )
                    yield from self.named_entities(subtree)

    def match(
        self, subtree: Span, possible_subject, exclusive_search: bool = True
    ) -> typing.Iterator[typing.Dict[str, typing.Any]]:
        for match_id, start, end in self.matcher(subtree):
            span = subtree[start:end]
            pos_label = self.nlp.vocab[match_id].text
            if exclusive_search:
                # phrases should stem from nsubj directly
                if possible_subject not in span:
                    continue

                # VERB-based phrases shoulb be of specific finegrained pos
                if "VERB" in pos_label and not any(
                    is_vbg(token) or is_vbn(token) for token in span
                ):
                    continue
                yield {
                    "entity_type": "noun phrase",
                    "label": pos_label,
                    "match": span.text,
                    "match_processed": " ".join(
                        t.lemma_.lower() for t in span if not t.is_punct
                    ),
                    "span_location": [span.start_char, span.end_char],
                }

    def named_entities(
        self, subtree: Span
    ) -> typing.Iterator[typing.Dict[str, typing.Any]]:
        for en in subtree.ents:
            yield {
                "entity_type": "named entity",
                "label": en.label_,
                "match": en.text,
                "match_processed": " ".join(
                    t.lemma_.lower() for t in en if not t.is_punct
                ),
                "span_location": [en.start_char, en.end_char],
            }


def create_nlp(model: str = "ru_core_news_sm") -> spacy.language.Language:
    return spacy.load(model)


nlp = create_nlp()


def create_pipeline(matcher: typing.Optional[Matcher] = None) -> ML:
    """Initializes ML pipeline."""
    return ML(nlp, matcher=matcher)
