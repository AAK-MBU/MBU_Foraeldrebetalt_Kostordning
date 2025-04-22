"""This module contains the main process of the robot."""

import json
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement
from robot_framework.subprocesses.create_invoice import (
    create_and_save_invoice,
    create_invoice_handler,
)
from robot_framework.subprocesses.create_queue_items import (
    process_and_create_queue_items,
)
from robot_framework import config


# pylint: disable-next=unused-argument
def process(
    orchestrator_connection: OrchestratorConnection,
    queue_element: QueueElement | None = None,
) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")
    oc_args_json = json.loads(orchestrator_connection.process_arguments)

    # Handles the queue uploader
    if oc_args_json["process"] == "queue_uploader":
        orchestrator_connection.log_trace("Starting queue uploader.")
        process_and_create_queue_items(
            folder_path=config.FOLDER_PATH,
            orchestrator_connection=orchestrator_connection,
        )

    # Handles the queue
    if oc_args_json["process"] == "handle_queue":
        orchestrator_connection.log_trace("Starting queue handler.")
        if not queue_element:
            orchestrator_connection.log_error("No queue element provided.")
            raise ValueError("No queue element provided.")

        orchestrator_connection.log_trace("Processing queue element.")
        queue_element_data = json.loads(queue_element.data)

        try:
            invoice_obj = create_invoice_handler(orchestrator_connection)
            create_and_save_invoice(
                invoice_obj, queue_element_data, orchestrator_connection
            )
        except Exception as error:
            print(f"Error in invoice processing: {error}")
            raise
