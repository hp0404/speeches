# -*- coding: utf-8 -*-
"""HTU's implementation of Penn Treebank's verb-related tags."""
import spacy


def is_vb(token: spacy.tokens.token.Token) -> bool:
    """Checks if token is VBN (verb, base form).
    Parameters
    ----------
    token: spacy.tokens.token.Token
        possible vbn token
    Returns
    -------
    bool : True if complies with our definition of VBD False otherwise.
    """
    return token.text == token.lemma_


def is_vbd(token: spacy.tokens.token.Token) -> bool:
    """Checks if token is VBN (verb, past tense).
    Parameters
    ----------
    token: spacy.tokens.token.Token
        possible vbn token
    Returns
    -------
    bool : True if complies with our definition of VBD False otherwise.
    """
    morph = token.morph.to_dict()
    return morph.get("Tense", "").lower() == "past"


def is_vbg(token: spacy.tokens.token.Token) -> bool:
    """Checks if token is VBG (verb, gerund or present participle).
    Parameters
    ----------
    token: spacy.tokens.token.Token
        possible vbg token
    Returns
    -------
    bool : True if complies with our definition of VBG False otherwise.
    """
    morph = token.morph.to_dict()
    is_gerund = morph.get("VerbForm", "").lower() == "conv"
    is_pres_part = (
        morph.get("VerbForm", "").lower() == "part"
        and morph.get("Tense", "").lower() == "pres"
    )
    return is_gerund or is_pres_part


def is_vbn(token: spacy.tokens.token.Token) -> bool:
    """Checks if token is VBN (verb, past participle).
    Parameters
    ----------
    token: spacy.tokens.token.Token
        possible vbn token
    Returns
    -------
    bool : True if complies with our definition of VBN False otherwise.
    """
    morph = token.morph.to_dict()
    return (
        morph.get("VerbForm", "").lower() == "part"
        and morph.get("Tense", "").lower() == "past"
    )


def is_vbp(token: spacy.tokens.token.Token) -> bool:
    """Checks if token is VBP (verb, non-3rd person, singular, present).
    Parameters
    ----------
    token: spacy.tokens.token.Token
        possible vbp token
    Returns
    -------
    bool : True if complies with our definition of VBP False otherwise.
    """
    morph = token.morph.to_dict()
    return (
        morph.get("Person", "").lower() != "third"
        and morph.get("Tense", "").lower() == "pres"
        and morph.get("Number", "").lower() == "sing"
    )


def is_vbz(token: spacy.tokens.token.Token) -> bool:
    """Checks if token is VBZ (verb, 3rd person, singular, present).
    Parameters
    ----------
    token: spacy.tokens.token.Token
        possible vbz token
    Returns
    -------
    bool : True if complies with our definition of VBZ False otherwise.
    """
    morph = token.morph.to_dict()
    return (
        morph.get("Person", "").lower() == "third"
        and morph.get("Tense", "").lower() == "pres"
        and morph.get("Number", "").lower() == "sing"
    )
