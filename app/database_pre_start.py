# -*- coding: utf-8 -*-
"""This module contains prestart script that checks if
the database is awake and running."""
import logging
from typing import Final

from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import get_settings
from app.db.database import get_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_TRIES: Final = 60 * 5  # 5 minutes
WAIT_SECONDS: Final = 1


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_SECONDS),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    """Tries to create session to check if database is awake."""
    try:
        settings = get_settings()
        with Session(get_engine(settings)) as session:
            session.exec(select(1))
    except Exception as generic_exception:
        logger.error(generic_exception)
        raise generic_exception


def main() -> None:
    """Tests database connection."""
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
