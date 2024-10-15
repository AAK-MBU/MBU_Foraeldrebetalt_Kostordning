"""This module contains the main process of the robot."""
import os
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from robot_framework.subprocesses.helper_functions import SAPApplication
from robot_framework.subprocesses.sap_create_invoice import InvoiceHandler
from robot_framework.initialize import initialize


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    sap_app_obj = SAPApplication(orchestrator_connection=orchestrator_connection)
    sap_session = sap_app_obj.get_session(session_number=0)

    invoice_obj = InvoiceHandler(sap_session)

    orchestrator_connection.log_trace("Create invoice.")
    invoice_obj.create_invoice(
        business_partner_id="",
        content_type="",
        base_system_id="",
        name_person="",
        start_date="",
        end_date="",
        main_transaction_id="",
        main_transaction_amount="",
        sub_transaction_id="",
        sub_transaction_fee_adm_id="",
        sub_transaction_fee_adm_amount="",
        sub_transaction_fee_inst_id="",
        sub_transaction_fee_inst_amount="",
        payment_recipient_identifier="",
        service_recipient_identifier=""
    )
