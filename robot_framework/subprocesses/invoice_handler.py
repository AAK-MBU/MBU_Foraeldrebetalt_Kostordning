"""This module contains a class and functions relating to creating an invoice in SAP."""

import time

from robot_framework.exceptions import BusinessError


class InvoiceHandler:
    """
    A class used to create invoices in SAP.

    Attributes:
    ----------
    session : object
        The session object to interact with SAP.
    """

    def __init__(self, session):
        """
        Initialize the InvoiceCreator with a session object.

        Parameters:
        ----------
        session : object
            The session object to interact with SAP.
        """
        self.session = session

    def open_business_partner(
        self, business_partner_id: str, content_type: str, base_system_id: str
    ):
        """
        Open a business partner in SAP.

        Parameters:
        ----------
        business_partner_id : str
            ID of the business partner.
        content_type : str
            Content type.
        base_system_id : str
            Base system ID.
        """
        self.session.findById("wnd[0]/usr/ctxtLV_BP_IN").text = business_partner_id
        self.session.findById("wnd[0]/usr/ctxtP_IHS_IN").text = content_type
        self.session.findById("wnd[0]/usr/txtP_NBS_IN").text = base_system_id
        self.session.findById("wnd[0]/tbar[1]/btn[8]").press()

        time.sleep(2)
        # Check if popup window exists
        try:
            popup = self.session.findById("/app/con[0]/ses[0]/wnd[1]")
            if popup:
                error_message = popup.findById("usr/txtMESSTXT1").text
                # If popup exists, check the message and click the button
                if "CPR-nr:" in error_message:
                    popup.findById("tbar[0]/btn[0]").press()
                    raise BusinessError(
                        f"Business partner {business_partner_id} not found in SAP: {error_message}"
                    )
        except BusinessError as be:
            print(f"Business error while checking popup: {be}")
            raise
        except Exception:  # pylint: disable=broad-except
            # If popup does not exist, continue
            pass

    def _create_invoice_row(
        self,
        row_index: int,
        amount: str,
        start_date: str,
        end_date: str,
        main_transaction_id: str,
        sub_transaction_id: str,
        name_person: str,
        payment_recipient_identifier: str,
        service_recipient_identifier: str,
        business_partner_id: str,
    ) -> None:
        """
        Create a row in the invoice.

        Parameters:
        ----------
        row_index : int
            Index of the row in the table.
        amount : str
            Amount for the transaction.
        start_date : str
            Start date of the transaction period.
        end_date : str
            End date of the transaction period.
        main_transaction_id : str
            ID of the main transaction.
        sub_transaction_id : str
            ID of the sub-transaction.
        name_person : str
            Name of the person.
        payment_recipient_identifier : str
            Identifier of the payment recipient.
        service_recipient_identifier : str
            Identifier of the service recipient.
        business_partner_id : str
            ID of the business partner.
        """
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/txtWA_FAKTURALINIE-BELOEB[4,{row_index}]"
        ).text = amount
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-LINJE_PERIODE_FRA[6,{row_index}]"
        ).text = start_date
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-LINJE_PERIODE_TIL[7,{row_index}]"
        ).text = end_date
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-HOVED_TRANS[9,{row_index}]"
        ).text = main_transaction_id
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-DEL_TRANS[10,{row_index}]"
        ).text = sub_transaction_id
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-FORFALDSDATO[12,{row_index}]"
        ).text = start_date
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-STIFTELSESDATO[13,{row_index}]"
        ).text = start_date
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/txtWA_FAKTURALINIE-POSTERINGSTEKST[17,{row_index}]"
        ).text = name_person
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-BETALINGS_MODT_KODE[18,{row_index}]"
        ).text = payment_recipient_identifier
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/txtWA_FAKTURALINIE-BETALINGS_MODT[19,{row_index}]"
        ).text = business_partner_id
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/ctxtWA_FAKTURALINIE-YDELSES_MODT_KODE[20,{row_index}]"
        ).text = service_recipient_identifier
        self.session.findById(
            f"wnd[0]/usr/tblSAPLZDKD0068_MODTAGKRAVDIAFAKTLINJECTR/txtWA_FAKTURALINIE-YDELSES_MODT[21,{row_index}]"
        ).text = business_partner_id
        self.session.findById("wnd[0]").sendVKey(0)

    def create_invoice(
        self,
        business_partner_id: str,
        content_type: str,
        base_system_id: str,
        name_person: str,
        start_date: str,
        end_date: str,
        main_transaction_id: str,
        main_transaction_amount: str,
        sub_transaction_id: str,
        sub_transaction_fee_adm_id: str,
        sub_transaction_fee_adm_amount: str,
        sub_transaction_fee_inst_id: str,
        sub_transaction_fee_inst_amount: str,
        payment_recipient_identifier: str,
        service_recipient_identifier: str,
    ):
        """
        Create an invoice with multiple rows.

        Parameters:
        ----------
        business_partner_id : str
            ID of the business partner.
        content_type : str
            Content type.
        base_system_id : str
            Base system ID.
        name_person : str
            Name of the person.
        start_date : str
            Start date of the transaction period.
        end_date : str
            End date of the transaction period.
        main_transaction_id : str
            ID of the main transaction.
        main_transaction_amount : str
            Amount for the main transaction.
        sub_transaction_id : str
            ID of the sub-transaction.
        sub_transaction_fee_adm_id : str
            ID of the sub-transaction for administration fee.
        sub_transaction_fee_adm_amount : str
            Amount for the sub-transaction administration fee.
        sub_transaction_fee_inst_id : str
            ID of the sub-transaction for institution fee.
        sub_transaction_fee_inst_amount : str
            Amount for the sub-transaction institution fee.
        payment_recipient_identifier : str
            Identifier of the payment recipient.
        service_recipient_identifier : str
            Identifier of the service recipient.
        """
        try:
            self.open_business_partner(
                business_partner_id, content_type, base_system_id
            )
        except BusinessError as be:
            print(f"Business error while opening business partner: {be}")
            raise
        except Exception as e:
            print(f"Error opening business partner: {e}")
            raise

        try:
            self.session.findById(
                "wnd[0]/usr/ctxtZDKD0312MODTAGKRAV_UDVEKSLE-FORFALDSDATO"
            ).text = start_date
        except Exception as e:
            print(f"Error setting due date: {e}")
            raise

        # Main transaction row
        try:
            self._create_invoice_row(
                0,
                main_transaction_amount,
                start_date,
                end_date,
                main_transaction_id,
                sub_transaction_id,
                name_person,
                payment_recipient_identifier,
                service_recipient_identifier,
                business_partner_id,
            )
        except Exception as e:
            self.session.findById("/app/con[0]/ses[0]/wnd[0]/tbar[0]/btn[3]").press()
            print(f"Error creating main transaction row. {e}")
            raise

        # Insert new line
        try:
            self.session.findById("wnd[0]/usr/btnINDSAETTXTBTN").press()
        except Exception as e:
            self.session.findById("/app/con[0]/ses[0]/wnd[0]/tbar[0]/btn[3]").press()
            print(f"Error inserting new line. {e}")
            raise

        # Sub administration fee row
        try:
            self._create_invoice_row(
                1,
                sub_transaction_fee_adm_amount,
                start_date,
                end_date,
                main_transaction_id,
                sub_transaction_fee_adm_id,
                name_person,
                payment_recipient_identifier,
                service_recipient_identifier,
                business_partner_id,
            )
        except Exception as e:
            self.session.findById("/app/con[0]/ses[0]/wnd[0]/tbar[0]/btn[3]").press()
            print(f"Error creating sub administration fee row. {e}")
            raise

        # Insert new line
        try:
            self.session.findById("wnd[0]/usr/btnINDSAETTXTBTN").press()
        except Exception as e:
            self.session.findById("/app/con[0]/ses[0]/wnd[0]/tbar[0]/btn[3]").press()
            print(f"Error inserting new line. {e}")
            raise

        # Sub institution fee row
        try:
            self._create_invoice_row(
                2,
                sub_transaction_fee_inst_amount,
                start_date,
                end_date,
                main_transaction_id,
                sub_transaction_fee_inst_id,
                name_person,
                payment_recipient_identifier,
                service_recipient_identifier,
                business_partner_id,
            )
        except Exception as e:
            self.session.findById("/app/con[0]/ses[0]/wnd[0]/tbar[0]/btn[3]").press()
            print(f"Error creating sub institution fee row. {e}")
            raise

    def save_invoice(self):
        """
        Save the invoice in SAP.

        This function sends a key press to save the invoice.
        """
        try:
            self.session.findById("/app/con[0]/ses[0]/wnd[0]/tbar[0]/btn[11]").press()
            time.sleep(1)
            self.session.findById("/app/con[0]/ses[0]/wnd[1]/tbar[0]/btn[0]").press()
        except Exception as e:
            self.session.findById("/app/con[0]/ses[0]/wnd[0]/tbar[0]/btn[3]").press()
            print(f"Error saving invoice. {e}")
            raise
