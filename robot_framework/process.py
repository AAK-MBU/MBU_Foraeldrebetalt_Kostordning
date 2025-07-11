"""Module contains the main process of the robot."""

import json

from OpenOrchestrator.database.queues import QueueElement
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

from robot_framework.exceptions import BusinessError
from robot_framework.subprocesses.check_termination_date import check_termination_date
from robot_framework.subprocesses.create_invoice import (
    create_and_save_invoice,
    create_invoice_handler,
)


def process(
    orchestrator_connection: OrchestratorConnection,
    queue_element: QueueElement | None = None,
) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    orchestrator_connection.log_trace("Starting queue handler.")
    if not queue_element:
        msg = "No queue element provided."
        orchestrator_connection.log_error(msg)
        raise ValueError(msg)

    if queue_element.data is None:
        msg = "Queue element data is None."
        orchestrator_connection.log_error(msg)
        raise ValueError(msg)
    queue_element_data = json.loads(queue_element.data)

    orchestrator_connection.log_trace(
        f"Processing queue element: {queue_element.reference}",
    )

    # Check if the termination date is set
    if check_termination_date(queue_element_data.get('start_date'), queue_element_data):
        orchestrator_connection.log_error(
            f"Termination date {queue_element_data.start_date} is greater than registration date {queue_element_data.start_date}.",
        )
        msg = f"Termination date {queue_element_data.start_date} is greater than registration date {queue_element_data.start_date}."
        raise BusinessError(msg)

    # Create and save the invoice
    orchestrator_connection.log_trace("Creating invoice.")
    try:
        invoice_obj = create_invoice_handler(orchestrator_connection)
        create_and_save_invoice(
            invoice_obj, queue_element_data, orchestrator_connection,
        )
    except BusinessError as error:
        orchestrator_connection.log_error(f"Business error: {error}")
        raise
    except Exception as error:
        orchestrator_connection.log_error(f"Error processing invoice: {error}")
        raise
