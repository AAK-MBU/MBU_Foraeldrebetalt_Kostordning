"""MISSING"""
import pyodbc

orchestrator_connection.log_trace("Check for deregistration.")
check_for_deregistration(orchestrator_connection)

def check_for_deregistration(oc: OrchestratorConnection, snn: str, institution_number: str, start_date: str):
    """MISSING"""
    conn_str = oc.get_constant('DbConnectionString').value
    conn = pyodbc.connect(conn_str)

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM [rpa].[fn_GetUdmeldelse]('{snn}','{institution_number}','{start_date}')")
    record = cursor.fetchall()

    print(record)
