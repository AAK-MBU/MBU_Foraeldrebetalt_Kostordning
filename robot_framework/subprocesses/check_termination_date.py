"""This module checks if there are any terminations in the database that occurred before the start date"""

import os
import logging
from datetime import datetime, date
from typing import Mapping, Any, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def parse_ddmmyy_to_date(ddmmyy: str) -> date:
    """
    Parse 'ddmmyy' (e.g., '010725') into a date object (2025-07-01).
    """
    if not ddmmyy or len(ddmmyy) != 6 or not ddmmyy.isdigit():
        raise ValueError(
            f"start_dato '{ddmmyy}' is not in expected 'ddmmyy' numeric format."
        )
    try:
        return datetime.strptime(ddmmyy, "%d%m%y").date()
    except ValueError as exc:
        raise ValueError(f"Could not parse start_dato '{ddmmyy}': {exc}") from exc


def check_termination_date(
    start_dato_ddmmyy: str,
    queue_element_data: Mapping[str, Any],
    engine: Optional[Engine] = None,
) -> bool:
    """
    Return True if there exists a row in rpa.udmeldelserDT for the given CPR and institution number
    where udmldato < start_dato (start_dato provided as 'ddmmyy').

    :param start_dato_ddmmyy: Date in 'ddmmyy' format (e.g., '010725').
    :param queue_element_data: Mapping containing 'base_system_id' and 'institution_number'.
    :param engine: Optional SQLAlchemy Engine; if None, created from env var.
    """
    if not queue_element_data:
        raise ValueError("queue_element_data must be provided and non-empty.")

    try:
        cpr = queue_element_data["base_system_id"]
    except KeyError as exc:
        raise ValueError(
            "queue_element_data missing required key 'base_system_id'."
        ) from exc

    try:
        instnr = queue_element_data["institution_number"]
    except KeyError as exc:
        raise ValueError(
            "queue_element_data missing required key 'institution_number'."
        ) from exc

    start_date = parse_ddmmyy_to_date(start_dato_ddmmyy)

    if engine is None:
        db_url = os.getenv("OpenOrchestratorConnStringTest")
        if not db_url:
            raise EnvironmentError(
                "Database connection string not set in environment variable "
                "'OpenOrchestratorConnString'."
            )
        engine = create_engine(db_url, future=True)

    sql = text(
        """
        SELECT TOP 1 1
        FROM rpa.udmeldelserDT
        WHERE cpr = :cpr
          AND instnr = :instnr
          AND TRY_CONVERT(date, udmldato) < :start_date
        """
    )

    with engine.connect() as connection:
        row = connection.execute(
            sql,
            {
                "cpr": cpr,
                "instnr": instnr,
                "start_date": start_date,
            },
        ).first()

    exists = row is not None
    logging.debug(
        "check_termination_before_start: cpr=%s instnr=%s start_date=%s exists=%s",
        cpr,
        instnr,
        start_date.isoformat(),
        exists,
    )
    return exists
