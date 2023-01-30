# -*- coding: utf-8 -*-
import typing

import ruts  # type: ignore

from app.schemas import TextStatisticsJSON


def calculate_stats(sentence: str) -> typing.Optional[TextStatisticsJSON]:
    try:
        basic_stats = {
            k: v
            for k, v in ruts.BasicStats(sentence).get_stats().items()
            if k not in ["n_spaces", "n_sents", "c_syllables", "c_letters"]
        }
        readability = ruts.ReadabilityStats(sentence).get_stats()
        diversity = ruts.DiversityStats(sentence).get_stats()
        di = {
            **basic_stats,
            **readability,
            **diversity,
        }
        di.update(morphology=ruts.MorphStats(sentence).get_stats())
        data = TextStatisticsJSON(**di)
    except (AttributeError, ValueError):
        data = None
    return data
