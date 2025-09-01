from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from math import e
import re
import smtplib
from tkinter import SE
import pyodbc

class CertificateExpiryNotifier:
    def __init__(
        self,
        db_connection_string,
        smtp_server,
        smtp_port,
        email_username,
        email_password,
    ):
        """
        Initialize the Certificate Expiry Notifier

        Args:
            db_connection_string: SQL Server connection string
            smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
            smtp_port: SMTP port (usually 587 for TLS)
            email_username: Email address for authentication
            email_password: Email password or app password
        """
        self.db_connection_string = db_connection_string
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_username = email_username
        self.email_password = email_password
        self.sender_name = "Devanshu Agarwal"

    def process_expired_certificates(self):
        """
        Main method to process expired certificates and send notifications
        """
        print("Checking for expired certificates...")
        expired_certs = self.get_expired_certificates()

        if not expired_certs:
            print("No expired certificates found.")
            return

        group_expired_certs = self.grouping_certificates_via_owners(expired_certs)

        print(f"Found {len(expired_certs)} expired certificate(s)")

        for owner in group_expired_certs:
            # create email body
            email_body = self.create_email_body(group_expired_certs[owner])
            subject = "Certificate Expiration Notification"

            # extract emails from owner contact details
            self.send_email(owner, subject, email_body)

    def get_expired_certificates(self):
        try:
            conn = pyodbc.connect(self.db_connection_string)
            cursor = conn.cursor()

            # Query to get expired certificates where Active = 1
            query = """
            SELECT [SR NO], [Certificate Name], [Issued To], [Issued By], 
                   [Domain], [Issuing Date], [Expire date], [Type], 
                   [Owner], [Owner Contact Details], [Comment], [Issued], [Active]
            FROM CLM_Table 
            WHERE [Expire date] < GETDATE() AND [Active] = 'Yes'
            """

            cursor.execute(query)
            expired_certs = cursor.fetchall()

            # Convert to list of dictionaries for easier handling
            columns = [desc[0] for desc in cursor.description]
            result = []
            for row in expired_certs:
                cert_dict = dict(zip(columns, row))
                result.append(cert_dict)

            conn.close()
            return result

        except Exception as e:
            print(f"Database error: {str(e)}")
            return []

    def grouping_certificates_via_owners(self, expired_certs):
        group_certificates = {}
        for cert in expired_certs:
            receivers = cert.get("Owner") + (
                cert.get("Issued To") if cert.get("Issued To") else ""
            )

            # Check if Owner and Issued To are the same or similar
            if cert.get("Owner") == cert.get("Issued To"):
                receivers = cert.get("Owner")
            elif cert.get("Owner") in cert.get("Issued To"):
                receivers = cert.get("Issued To")
            elif cert.get("Issued To") in cert.get("Owner"):
                receivers = cert.get("Owner")
            else:
                receivers = cert.get("Owner") + "," + cert.get("Issued To")

            # Group certificates by receivers
            if receivers in group_certificates:
                group_certificates[receivers].append(cert)
            else:
                group_certificates[receivers] = [cert]

        return group_certificates

    def create_email_body(self, cert_data):
        """
        Create HTML email body with certificate details

        Args:
            cert_data: Dictionary containing certificate information

        Returns:
            HTML formatted email body
        """
        html_body = f"""
            <html>
                <body>
                    <p>Dear Team,</p>
            
                    <p>This is to inform you that the following certificate has <strong>expired</strong>. 
                    Please take immediate action to renew or replace this certificate to avoid any service disruptions.</p>
            
                    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
                        <tr style="background-color: #f2f2f2;">
                            <th style="text-align: left;">Certificate Name/Common NameField</th>
                            <th style="text-align: left;">Type</th>
                            <th style="text-align: left;">Expiry Date</th>
                            <th style="text-align: left;">Owner</th>
                            <th style="text-align: left;">Issued To</th>
                            <th style="text-align: left;">Associated REQ Number</th>
                        </tr>
            
            """
        for cert in cert_data:
            html_body += f"""     
                <tr>
                        <td>{cert.get('Certificate Name', 'N/A') }</td>
                        <td>{cert.get('Type', 'N/A')}</td>
                        <td style="color: red; font-weight: bold;">{cert.get('Expire date', 'N/A')}</td>
                        <td>{cert.get('Owner', 'N/A')}</td>
                        <td>{cert.get('Issued To', 'N/A')}</td>
                        <td>{cert.get('Comment', 'N/A')}</td>
                </tr>
                        """

        html_body += f"""
                    </table>
            
                    <p>Please prioritize the renewal of this certificate to ensure continued security and functionality.</p>
            
                    <p>Best regards,<br>
                    <strong>Devanshu Agarwal</strong><br>
                    IT Security Team</p>
                </body>
        </html>
        """
        return html_body

    def send_email(self, recipient_emails, subject, body):
        """
        Send email to recipient

        Args:
            recipient_email: Email address of recipient
            subject: Email subject
            body: HTML email body

        Returns:
            True if successful, False otherwise
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_username
            msg["To"] = recipient_emails

            # Add HTML body
            html_part = MIMEText(body, "html")
            msg.attach(html_part)

            # Connect to server and send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)

            text = msg.as_string()
            server.sendmail(self.email_username, recipient_emails.split(','), text)
            server.quit()

            print(f"Email sent successfully to {recipient_emails}")
            return True

        except Exception as e:
            print(f"Failed to send email to {recipient_emails}: {str(e)}")
            return False


# Program entry point
if __name__ == "__main__":
    # Database connection string
    db_connection_string = "Driver={SQL Server};Server=localhost\\SQLEXPRESS;Database=CLM;Trusted_Connection=True"

    # SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_username = "devanshugrwl@gmail.com"
    email_password = "<REMOVED PASSWORD>"  # Use an app password for better security

    notifier = CertificateExpiryNotifier(
        db_connection_string, smtp_server, smtp_port, email_username, email_password
    )
    notifier.process_expired_certificates()
