"""Module for managing SAP application sessions and login using SAP CLI."""

from itk_dev_shared_components.sap import sap_login, multi_session


class SAPApplication:
    """Class to manage the interaction with SAP applications, including login and session handling."""

    def __init__(self, orchestrator_connection):
        """
        Initialize the SAPApplication instance with an orchestrator connection.

        Args:
            orchestrator_connection: The connection object to the orchestrator system, used for logging and retrieving credentials.
        """
        self.orchestrator_connection = orchestrator_connection

    def open_sap(self):
        """
        Open the SAP system by logging in using the provided credentials from the orchestrator.

        Retrieves the SAP credentials stored in the orchestrator system and uses them to log in to the SAP system via the CLI.
        """
        self.orchestrator_connection.log_trace("Open SAP.")
        creds_sap = self.orchestrator_connection.get_credential("sap_kostordning")
        sap_login.login_using_cli(
            username=creds_sap.username,
            password=creds_sap.password,
            client='751',
            system='P02',
            timeout=60
        )

    def get_session(self, session_number: int):
        """
        Retrieve an SAP session by session number.

        Args:
            session_number (int): The index of the session to retrieve.

        Returns:
            session: The session object corresponding to the given session number.
        """
        self.orchestrator_connection.log_trace("Get SAP session.")
        sessions = multi_session.get_all_sap_sessions()
        session = sessions[session_number]

        return session
