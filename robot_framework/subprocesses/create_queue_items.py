"""
This script processes Excel files in a specified folder, extracting data from a specific sheet
"""

import os
import json
from datetime import datetime
import pandas as pd
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from dateutil.relativedelta import relativedelta
from robot_framework.config import QUEUE_NAME


def process_excel_files(
    folder_path: str, orchestrator_connection: OrchestratorConnection
) -> list:
    """
    Process Excel files in a folder, extracting data only from the sheet that matches
    next month's name and year in Danish (e.g., "maj 25").

    Stops reading when first column is empty or contains 'i alt' (case-insensitive).
    """
    all_data = []

    # Get next month and year (2-digit year)
    now = datetime.now()
    next_month_date = now + relativedelta(months=1)
    danish_months = [
        "jan",
        "feb",
        "mar",
        "apr",
        "maj",
        "jun",
        "jul",
        "aug",
        "sep",
        "okt",
        "nov",
        "dec",
    ]
    month_abbr = danish_months[next_month_date.month - 1]
    year_short = str(next_month_date.year)[-2:]
    target_sheet_name = f"{month_abbr} {year_short}"
    print(f"Target sheet name: {target_sheet_name}")

    for filename in os.listdir(folder_path):
        if filename.endswith((".xlsx", ".xls", ".xlsm")):
            file_path = os.path.join(folder_path, filename)
            try:
                xl = pd.ExcelFile(file_path)
                sheet_names_lower = [sheet.lower() for sheet in xl.sheet_names]

                if target_sheet_name.lower() not in sheet_names_lower:
                    orchestrator_connection.log_error(
                        f"Sheet '{target_sheet_name}' not found in {filename}"
                    )

                # Get the actual matching sheet name (case-sensitive)
                actual_sheet_name = next(
                    sheet
                    for sheet in xl.sheet_names
                    if sheet.lower() == target_sheet_name.lower()
                )

                # Read cell B1 for Hovedtrans
                hovedtrans_df = pd.read_excel(
                    file_path,
                    sheet_name=actual_sheet_name,
                    header=None,
                    nrows=1,
                    usecols="B",
                )
                hovedtrans_value = (
                    str(hovedtrans_df.iat[0, 0]).strip()
                    if pd.notna(hovedtrans_df.iat[0, 0])
                    else ""
                )

                # Read cell I1 for Institutionnumber
                institution_df = pd.read_excel(
                    file_path,
                    sheet_name=actual_sheet_name,
                    header=None,
                    nrows=1,
                    usecols="I",
                )
                institution_value = (
                    str(institution_df.iat[0, 0]).strip()
                    if pd.notna(institution_df.iat[0, 0])
                    else ""
                )

                # Read header rows (rows 3 & 4, index 2 & 3)
                headers_df = pd.read_excel(
                    file_path,
                    sheet_name=actual_sheet_name,
                    header=None,
                    nrows=2,
                    skiprows=2,
                    usecols="A:J",
                )
                row1 = headers_df.iloc[0]
                row2 = headers_df.iloc[1]

                combined_headers = [
                    (
                        f"{str(r1).strip()} {str(r2).strip()}"
                        if pd.notna(r2)
                        else str(r1).strip()
                    )
                    for r1, r2 in zip(row1, row2)
                ]
                cleaned_headers = [
                    col.replace(":", "").replace(".", "").strip()
                    for col in combined_headers
                ]
                cleaned_headers = [col.lower() for col in cleaned_headers]

                # Read the actual data rows starting at row 5
                data_df = pd.read_excel(
                    file_path,
                    sheet_name=actual_sheet_name,
                    header=None,
                    skiprows=4,
                    usecols="A:J",
                    dtype=str,
                )
                data_df.columns = cleaned_headers
                data_df.dropna(axis=1, how="all", inplace=True)
                data_df = data_df.loc[:, data_df.columns.notna()]
                data_df = data_df.loc[:, data_df.columns != ""]
                data_df.fillna("", inplace=True)

                # Stop reading at first empty or 'i alt' in first column
                first_col = data_df.columns[0]
                stop_index = None
                for i, val in enumerate(data_df[first_col]):
                    if val.strip() == "" or "i alt" in val.strip().lower():
                        stop_index = i
                        break
                if stop_index is not None:
                    data_df = data_df.iloc[:stop_index]

                # Convert to dicts and enrich with metadata
                records = data_df.to_dict(orient="records")
                for idx, record in enumerate(records, start=1):
                    record["hovedtrans"] = hovedtrans_value
                    record["institutionnumber"] = institution_value
                    record["rownumber"] = idx

                all_data.extend(records)
                print(
                    f"Processed: {filename} (sheet: '{actual_sheet_name}', {len(records)} rows)"
                )

            # pylint: disable-next = broad-exception-caught
            except Exception as e:
                print(f"Error processing {filename}. {e}")

    return all_data


def create_queue_items(
    folder_path: str, orchestrator_connection: OrchestratorConnection
) -> list:
    """
    This function would contain the logic to create queue items in your system
    For now, we'll just print the data to simulate this process

    arguments:
    folder_path : str
        The path to the folder containing the Excel files.

    returns:
    list of dicts
        A list of dictionaries where each dictionary represents a queue item.
    """
    excel_data = process_excel_files(
        folder_path=folder_path, orchestrator_connection=orchestrator_connection
    )

    queue_items = []
    for row in excel_data:
        queue_item = {
            "business_partner_id": row.get("betalers cpr-nr"),
            "content_type": "FBEK",
            "base_system_id": row.get("barnets cpr-nr"),
            "name_person": row.get("barnets navn"),
            "start_date": row.get("start"),
            "end_date": row.get("slut"),
            "main_transaction_id": row.get("hovedtrans"),
            "main_transaction_amount": row.get("beløb"),
            "sub_transaction_id": row.get("hovedtrans"),
            "sub_transaction_fee_adm_id": "ADMG",
            "sub_transaction_fee_adm_amount": row.get("gebyr (adm)"),
            "sub_transaction_fee_inst_id": "INSG",
            "sub_transaction_fee_inst_amount": row.get("gebyr (ins)"),
            "payment_recipient_identifier": "02",
            "service_recipient_identifier": "02",
            "row_number": row.get("rownumber"),
        }
        queue_items.append(queue_item)

    return queue_items


def add_queue_items_to_orchestrator(
    queue_items: list, orchestrator_connection: OrchestratorConnection
) -> None:
    """
    This function would contain the logic to add queue items to your orchestrator
    For now, we'll just print the data to simulate this process"
    """
    current_month_year = datetime.now().strftime("%m%Y")
    all_ref = [
        (
            data.get("main_transaction_id", "unknown")
            + "_"
            + current_month_year
            + "_"
            + str(data.get("row_number", ""))
        )
        for data in queue_items
    ]

    data_json = [json.dumps(data, ensure_ascii=False) for data in queue_items]
    try:
        orchestrator_connection.bulk_create_queue_elements(
            queue_name=QUEUE_NAME,
            references=all_ref,
            data=data_json,
            created_by=os.getlogin(),
        )
    except Exception as e:
        orchestrator_connection.log_error(
            f"Error adding queue items to orchestrator: {e}"
        )
        raise
    orchestrator_connection.log_info(
        f"Total number of queue items added: {len(queue_items)} item(s)"
    )


def process_and_create_queue_items(
    folder_path: str, orchestrator_connection: OrchestratorConnection
) -> None:
    """
    Main function to process Excel files and create queue items in the specified folder.
    """
    orchestrator_connection.log_info(f"Processing Excel files in folder: {folder_path}")
    orchestrator_connection.log_info("Creating queue items...")
    items = create_queue_items(
        folder_path=folder_path, orchestrator_connection=orchestrator_connection
    )
    add_queue_items_to_orchestrator(
        queue_items=items, orchestrator_connection=orchestrator_connection
    )
    orchestrator_connection.log_info("Queue items created successfully.")
