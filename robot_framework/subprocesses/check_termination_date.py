"""Check if the termination date in the database is set."""

import os

from OpenOrchestrator.database.queues import QueueElement
from sqlalchemy import create_engine, text


def check_termination_date(termination_date: str, queue_element_data: QueueElement) -> bool:
    """Check if the termination date in the database is set.

    :param termination_date: The date to check against, typically 'ddmmyy'.
    :param queue_element_data: Data from the queue element, expected to contain
        'cpr' and 'instnr'.
    :return: True if any termination date is set, False otherwise.
    """
    db_url = os.getenv("OpenOrchestratorConnString")

    if not db_url:
        raise ValueError(
            "Database connection string not set in environment variable 'OpenOrchestratorConnString'",
        )
    if not termination_date:
        raise ValueError("Termination date is not provided or is empty.")
    if (
        not queue_element_data
        or "base_system_id" not in queue_element_data
        or "institution_number" not in queue_element_data
    ):
        raise ValueError("Queue element data must contain 'base_system_id' and 'institution_number' keys.")

    engine = create_engine(db_url)

    with engine.connect() as connection:
        query = text("""
            SELECT COUNT(*) FROM rpa.udmeldelserDT
            WHERE udmldato < :termination_date
            AND cpr = :cpr
            AND instnr = :instnr
        """)

        result = connection.execute(
            query,
            {
                "termination_date": termination_date,
                "cpr": queue_element_data.get('base_system_id'),
                "instnr": queue_element_data.get('institution_number'),
            },
        ).scalar()
        print(f"Query result: {result}")

    return (result or 0) > 0
