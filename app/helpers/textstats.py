# -*- coding: utf-8 -*-
import typing

import ruts

from app.schemas import TextStatisticsJSON


def calculate_stats(sentence: str) -> typing.Optional[TextStatisticsJSON]:
    try:
        data = TextStatisticsJSON(
            basic=ruts.BasicStats(sentence).get_stats(),
            readability=ruts.ReadabilityStats(sentence).get_stats(),
            diversity=ruts.DiversityStats(sentence).get_stats(),
            morphology=ruts.MorphStats(sentence).get_stats(),
        )
    except (AttributeError, ValueError):
        data = None
    return data
