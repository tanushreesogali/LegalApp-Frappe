import frappe
from frappe.model.document import Document
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class CaseMaster(Document):
    def notify_case_creation(self):
        smtp_server = "smtp.transmail.co.in"
        smtp_port = 587
        smtp_user = "emailapikey"
        smtp_password = (
            "PHtE6r1cF7jiim598RZVsPW9QMCkMN96/uNveQUTt4tGWPNRTk1U+tgokDO0rRx+UKZAHKPInos5tbqZtbiHdz6/"
            "Z2dED2qyqK3sx/VYSPOZsbq6x00as1wSc0TfUILscdds1CLfutnYNA=="
        )
        from_address = "noreply@merillife.com"
        to_address = self.email_address
        bcc_address = "rishi.hingad@merillife.com"

        subject = f"New Case Created: {self.case_number}"
        body = f"""
        Dear Team,

        A new case has been created in the system. Below are the details:

        Case Number: {self.case_number}
        Court Name: {self.court_name}
        Court City: {self.court_city_name}
        Court State: {self.court_state_name}
        Court Country: {self.court_country_name}

        Please review the case and take the necessary actions.

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
                print("Email sent successfully!")

                # Log the email
                doc = frappe.get_doc({
                    'doctype': 'Email Log',
                    'case_number': self.case_number,
                    'to_email': to_address,
                    'from_email': from_address,
                    'message': body,
                    'status': "Successfully Sent",
                    'screen': "Case Master Notification",
                    'created_by': from_address
                })
                doc.insert(ignore_permissions=True)
                frappe.db.commit()

        except Exception as e:
            print(f"Failed to send email: {e}")
            error_message = f"Failed to send email: {e}"
            doc = frappe.get_doc({
                'doctype': 'Email Log',
                'case_number': self.case_number,
                'to_email': to_address,
                'from_email': from_address,
                'message': body,
                'status': error_message,
                'screen': "Case Master Notification",
                'created_by': from_address
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()

# Hook-compatible wrapper function
def after_insert_notify(doc, method):
    doc.notify_case_creation()