import frappe
from frappe import _
from frappe.model.document import Document
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from frappe.exceptions import DoesNotExistError
from datetime import datetime, timedelta

class HearingDetails(Document):
    
    def validate(self):
        print(f"Debug: Validating HearingDetails: {self.name}, is_new={self.is_new()}")
        
        # Logic to track new hearing dates
        previous_dates = set()
        if not self.is_new():
            previous_doc = frappe.get_doc(self.doctype, self.name)
            previous_dates = {str(date) for date in {row.get("hearing_date") for row in previous_doc.get("hearing_date_table", [])} if date}

        current_dates = {str(row.get("hearing_date")) for row in self.get("hearing_date_table", []) if row.get("hearing_date")}
        new_dates = current_dates - previous_dates

        for date in new_dates:
            hearing_date_entry = next(
                (row for row in self.get("hearing_date_table", []) if str(row.get("hearing_date")) == date), 
                None
            )
            if hearing_date_entry:
                frappe.enqueue(
                    method=self.send_email_on_hearing_date_added, 
                    hearing_date_entry=hearing_date_entry, 
                    queue='default'
                )
                frappe.enqueue(
                    method=self.insert_hearing_date, 
                    hearing_date_entry=hearing_date_entry, 
                    queue='default'
                )
    
    def insert_hearing_date(self, hearing_date_entry):
        """This method will insert the hearing date document after the main document is saved."""
        try:
            hearing_date_doc = frappe.get_doc({
                "doctype": "Hearing Date",
                "case_link": self.case_no,
                "hearing_details_link": self.name,
                "hearing_date": hearing_date_entry.get("hearing_date")
            })
            hearing_date_doc.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            print(f"Failed to insert Hearing Date: {e}")
            frappe.log_error(message=f"Failed to insert Hearing Date for Hearing Details {self.name}: {e}", title="Hearing Date Insert Error")

    def send_email_on_hearing_date_added(self, hearing_date_entry):
        frappe.log_error(message=f"Triggered for hearing date: {hearing_date_entry}", title="Hearing Date Email Debug")
        smtp_server = "smtp.transmail.co.in"
        smtp_port = 587
        smtp_user = "emailapikey"
        smtp_password = "PHtE6r1cF7jiim598RZVsPW9QMCkMN96/uNveQUTt4tGWPNRTk1U+tgokDO0rRx+UKZAHKPInos5tbqZtbiHdz6/Z2dED2qyqK3sx/VYSPOZsbq6x00as1wSc0TfUILscdds1CLfutnYNA=="
        from_address = 'noreply@merillife.com'
        to_address = self.email_address
        bcc_address = "rishi.hingad@merillife.com"

        subject = f"New Hearing Date Added for Case {self.case_no}"
        body = f"""
        Dear Team,

        A new hearing date has been added for your Case Number: {self.case_no}.
        Hearing Detail Reference: {self.name}
        Hearing Date: {hearing_date_entry.get('hearing_date')}
        Details of Hearing: {hearing_date_entry.get('details_of_hearing')}

        Please update your records accordingly.

        Thank you.
        """

        msg = MIMEMultipart()
        msg["From"] = from_address
        msg["To"] = to_address
        msg["Subject"] = subject
        msg["Bcc"] = bcc_address
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(from_address, [to_address, bcc_address], msg.as_string())
                print("Email sent successfully for new hearing date!")

                doc = frappe.get_doc({
                    'doctype': 'Email Log',
                    'case_number': self.case_no,
                    'hearing_details': self.name,       
                    'to_email': to_address,
                    'from_email': from_address,
                    'message': body,
                    'status': "Successfully Sent",
                    'screen': "Hearing Details Notification",
                    'created_by': from_address
                })
                doc.insert(ignore_permissions=True)
                frappe.db.commit()

            return {
                "status": "success",
                "message": "Hearing reminder email sent successfully."
            }

        except Exception as e:
            print(f"Failed to send email: {e}")
            msge = f"Failed to send email: {e}"
            doc = frappe.get_doc({
                'doctype': 'Email Log',
                'case_number': self.case_no,
                'hearing_details': self.name,
                'to_email': to_address,
                'from_email': from_address,
                'message': body,
                'status': msge,
                'screen': "Hearing Details Notification",
                'created_by': from_address
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()

            return {
                "status": "fail",
                "message": "Failed to send email."
            }
        
    def send_reminder_emails(self):
        smtp_server = "smtp.transmail.co.in"
        smtp_port = 587
        smtp_user = "emailapikey"
        smtp_password = "PHtE6r1cF7jiim598RZVsPW9QMCkMN96/uNveQUTt4tGWPNRTk1U+tgokDO0rRx+UKZAHKPInos5tbqZtbiHdz6/Z2dED2qyqK3sx/VYSPOZsbq6x00as1wSc0TfUILscdds1CLfutnYNA=="
        from_address = 'noreply@merillife.com'
        bcc_address = "rishi.hingad@merillife.com"
        to_address = self.email_address

        print(f"Debug: Starting to send reminder emails for Case Number: {self.case_no}, Hearing Details: {self.name}")
        print(f"Debug: SMTP Server: {smtp_server}, Port: {smtp_port}, From Address: {from_address}, To Address: {to_address}")

        for entry in self.get('hearing_date_table', []):
            hearing_date = entry.get('hearing_date')
            print(f"Debug: Processing hearing date: {hearing_date}")

            if not hearing_date:
                print("Debug: Skipping entry due to missing hearing date.")
                continue

            try:
                hearing_date_obj = datetime.strptime(hearing_date, "%Y-%m-%d")
            except ValueError as ve:
                print(f"Debug: Invalid date format for hearing date: {hearing_date}, Error: {ve}")
                continue

            reminders = [
                (hearing_date_obj - timedelta(days=7), "7 days"),
                (hearing_date_obj - timedelta(days=5), "5 days"),
                (hearing_date_obj - timedelta(days=1), "1 day")
            ]
            print(f"Debug: Calculated reminders for hearing date {hearing_date}: {reminders}")

            for reminder_date, days_before in reminders:
                print(f"Debug: Checking if reminder date {reminder_date.date()} matches today's date {datetime.today().date()}")
                if reminder_date.date() == datetime.today().date():
                    print(f"Debug: Preparing to send reminder email for hearing date in {days_before}")
                    subject = f"Reminder: Hearing Date in {days_before} for Case {self.case_no}"
                    body = f"""
                    Dear Team,

                    This is a reminder that the hearing date for your Case Number: {self.case_no} is scheduled in {days_before}.
                    Hearing Date: {hearing_date}
                    Hearing Detail Reference: {self.name}

                    Please make necessary arrangements.

                    Thank you.
                    """
                    msg = MIMEMultipart()
                    msg["From"] = from_address
                    msg["To"] = self.email_address
                    msg["Subject"] = subject
                    msg["Bcc"] = bcc_address
                    msg.attach(MIMEText(body, "plain"))

                    try:
                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            server.starttls()
                            server.login(smtp_user, smtp_password)
                            server.sendmail(from_address, [self.email_address, bcc_address], msg.as_string())
                            print(f"Debug: Reminder email sent for hearing date in {days_before}!")

                            doc = frappe.get_doc({
                                'doctype': 'Email Log',
                                'case_number': self.case_no,
                                'hearing_details': self.name,
                                'to_email': to_address,
                                'from_email': from_address,
                                'message': body,
                                'status': "Successfully Sent",
                                'screen': "Hearing Details Notification",
                                'created_by': from_address
                            })
                            doc.insert(ignore_permissions=True)
                            frappe.db.commit()

                    except Exception as e:
                        print(f"Debug: Failed to send email for hearing date in {days_before}, Error: {e}")
                        msge = f"Failed to send email: {e}"
                        doc = frappe.get_doc({
                            'doctype': 'Email Log',
                            'case_number': self.case_no,
                            'hearing_details': self.name,
                            'to_email': to_address,
                            'from_email': from_address,
                            'message': body,
                            'status': msge,
                            'screen': "Hearing Details Notification",
                            'created_by': from_address
                        })
                        doc.insert(ignore_permissions=True)
                        frappe.db.commit()

    def on_update(self):
        self.send_reminder_emails()

@frappe.whitelist()
def get_events(start_date, end_date, filters=None): 
    if not filters:
        filters = {}

    # Fetch data from the database
    events = frappe.db.sql("""
        SELECT
            name AS id,
            hearing_date AS start,
            hearing_date AS end_date,
            hearing_details_link AS title,
            case_no || ' - ' || case_lawyer AS hearing_title
        FROM
            "tabHearing Details"
        WHERE
            hearing_date BETWEEN %(start)s AND %(end)s
    """, {"start": start_date, "end": end_date}, as_dict=True)

    return [
        {
            "id": event["id"],
            "start": event["start"],
            "end": event["end_date"],
            "title": event["title"],
            "hearing_title": event["hearing_title"],
        }
        for event in events
    ]

def send_email_wrapper(doc, method=None):
    # This assumes hearing_date_entry is a child table or something accessible via doc
    if hasattr(doc, 'hearing_date'):
        for hearing_date_entry in doc.hearing_date:
            doc.send_email_on_hearing_date_added(hearing_date_entry)
