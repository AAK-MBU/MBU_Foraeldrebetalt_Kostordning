"""This module defines any initial processes to run when the robot starts."""

import json
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from robot_framework.subprocesses.helper_functions import SAPApplication

def initialize(orchestrator_connection: OrchestratorConnection) -> None:
    """Do all custom startup initializations of the robot."""
    orchestrator_connection.log_trace("Initializing.")

    oc_args_json = json.loads(orchestrator_connection.process_arguments)
    transaction_code = oc_args_json['transactionCode']

    sap_app_obj = SAPApplication(orchestrator_connection=orchestrator_connection)

    sap_app_obj.open_sap()

    sap_session = sap_app_obj.get_session(session_number=0)
    sap_session.StartTransaction(transaction_code)

    orchestrator_connection.sap_session = sap_session
