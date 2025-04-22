"""
This module provides functionality to create and save invoices using the InvoiceHandler class.
It includes functions to create an invoice handler instance and to create and save an invoice based on data from a queue element.
"""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from robot_framework.subprocesses.invoice_handler import InvoiceHandler


def create_invoice_handler(orchestrator_connection: OrchestratorConnection) -> InvoiceHandler:
    """Create and return an InvoiceHandler instance."""
    try:
        return InvoiceHandler(orchestrator_connection.sap_session)
    except Exception as e:
        print(f"Error creating invoice handler: {e}")
        raise


def create_and_save_invoice(
    invoice_obj: InvoiceHandler,
    queue_element_data: dict,
    orchestrator_connection: OrchestratorConnection,
) -> None:
    """Create and save an invoice using the provided data."""
    try:
        orchestrator_connection.log_trace("Create invoice.")
        invoice_obj.create_invoice(
            business_partner_id=queue_element_data.get("business_partner_id"),
            content_type=queue_element_data.get("content_type"),
            base_system_id=queue_element_data.get("base_system_id"),
            name_person=queue_element_data.get("name_person"),
            start_date=queue_element_data.get("start_date"),
            end_date=queue_element_data.get("end_date"),
            main_transaction_id=queue_element_data.get("main_transaction_id"),
            main_transaction_amount=queue_element_data.get(
                "main_transaction_amount"
            ),
            sub_transaction_id=queue_element_data.get("main_transaction_id"),
            sub_transaction_fee_adm_id="ADMG",
            sub_transaction_fee_adm_amount=queue_element_data.get(
                "sub_transaction_fee_adm_amount"
            ),
            sub_transaction_fee_inst_id=queue_element_data.get(
                "sub_transaction_fee_inst_id"
            ),
            sub_transaction_fee_inst_amount=queue_element_data.get(
                "sub_transaction_fee_inst_amount"
            ),
            payment_recipient_identifier=queue_element_data.get(
                "payment_recipient_identifier"
            ),
            service_recipient_identifier=queue_element_data.get(
                "service_recipient_identifier"
            ),
        )
        invoice_obj.save_invoice()
        print("Invoice created successfully.")
        orchestrator_connection.log_trace("Invoice created.")
    except Exception as e:
        print(f"Error creating invoice: {e}")
        raise
