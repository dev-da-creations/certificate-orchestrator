from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import pyodbc
import os
from dotenv import load_dotenv


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
        Main method to process expiring and expired certificates, and send notifications
        """
        print("Checking for expiring and expired certificates...")
        filtered_certs = self.get_certificates_from_query()

        if not filtered_certs:
            print("No expired certificates found.")
            return

        # Group certificates by owners and days until expiry
        group_certificates_via_owners_and_days = (
            self.grouping_certificates_via_owners_and_days(filtered_certs)
        )

        subject = "!! IMPORTANT !! : Certificate Expiration Notification"
        # Send emails to each grouped owner with their respective certificates
        for owner in group_certificates_via_owners_and_days:
            if owner.__contains__("_Expired"):
                email_body = self.create_email_body(
                    group_certificates_via_owners_and_days[owner]
                )
                receivers = owner.replace("_Expired", "")
                print(
                    "Sending email to:",
                    receivers,
                    " whose certificates are already expired...\n",
                )
                self.send_email(receivers, subject, email_body)

            elif owner.__contains__("_Today"):
                email_body = self.create_email_body(
                    group_certificates_via_owners_and_days[owner]
                )
                receivers = owner.replace("_Today", "")
                print(
                    "Sending email to:",
                    receivers,
                    " whose certificates are expiring today...\n",
                )
                self.send_email(receivers, subject, email_body)

            elif owner.__contains__("_7days"):
                email_body = self.create_email_body(
                    group_certificates_via_owners_and_days[owner]
                )
                receivers = owner.replace("_7days", "")
                print(
                    "Sending email to:",
                    receivers,
                    " whose certificates are expiring in 7 days...\n",
                )
                self.send_email(receivers, subject, email_body)

            elif owner.__contains__("_14days"):
                email_body = self.create_email_body(
                    group_certificates_via_owners_and_days[owner]
                )
                receivers = owner.replace("_14days", "")
                print(
                    "Sending email to:",
                    receivers,
                    " whose certificates are expiring in 14 days...\n",
                )
                self.send_email(receivers, subject, email_body)

            else:
                email_body = self.create_email_body(
                    group_certificates_via_owners_and_days[owner]
                )
                receivers = owner.replace("_30days", "")
                print(
                    "Sending email to:",
                    receivers,
                    " whose certificates are expiring in 30 days...\n",
                )
                self.send_email(receivers, subject, email_body)

    def get_certificates_from_query(self):
        try:
            conn = pyodbc.connect(self.db_connection_string)
            cursor = conn.cursor()

            # Query to fetch certificates expiring in only next 30, 14, 7 days and already expired ones
            query = """
                SELECT [Certificate Name], [Issued To], [Issued By], [Issuing Date], [Expire date], [Type], 
                       [Owner], [Comment], [Active], DATEDIFF(day, GETDATE(), [Expire date])AS [Days Until Expiry]
                FROM CLM_Table 
                WHERE (
                    DATEDIFF(day, GETDATE(), [Expire date]) IN (0, 7, 14, 30)
                    OR DATEDIFF(day, GETDATE(), [Expire date]) < 0
                ) AND [Active] = 'Yes'
                """
            cursor.execute(query)
            expiring_certs = cursor.fetchall()

            # Convert to list of dictionaries for easier handling
            result = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in expiring_certs
            ]

            conn.close()

            return result

        except Exception as e:
            print(f"Database error: {str(e)}")
            return []

    def grouping_certificates_via_owners_and_days(self, filtered_certs):
        group_certificates = {}
        for cert in filtered_certs:
            # Normalize Owner and Issued To by removing spaces and converting to lowercase
            Owner = cert.get("Owner").lower().replace(" ", "")
            Issued_To = cert.get("Issued To").lower().replace(" ", "")

            # Check if Owner and Issued To are the same or similar and Days Until Expiry is in [7,14,30,0] or < 0
            if (
                cert.get("Days Until Expiry") in [7, 14, 30, 0]
                or cert.get("Days Until Expiry") < 0
            ):
                if Owner == Issued_To:
                    receivers = Owner
                elif Owner in Issued_To:
                    receivers = Issued_To
                elif Issued_To in Owner:
                    receivers = Owner
                else:
                    receivers = Owner + "," + Issued_To

                # Add expiry category to receivers
                if cert.get("Days Until Expiry") < 0:
                    receivers += "_Expired"
                elif cert.get("Days Until Expiry") == 0:
                    receivers += "_Today"
                elif cert.get("Days Until Expiry") == 7:
                    receivers += "_7days"
                elif cert.get("Days Until Expiry") == 14:
                    receivers += "_14days"
                else:
                    receivers += "_30days"

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
            
                    <p>This is to inform you that the following certificate"""

        # Check if multiple certificates are present and adjust wording accordingly        
        if len(cert_data) > 1:
            html_body += f"""s have <strong>expired</strong>."""
        else:
            html_body += f""" has <strong>expired</strong>."""

        html_body += f"""
                    Please take immediate action to renew or replace"""

        # Check if multiple certificates are present and adjust wording accordingly
        if len(cert_data) > 1:
            html_body += f""" these certificates"""
        else:
            html_body += f""" this certificate"""

        html_body += f""" to avoid any service disruptions.</p>
            
                    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
                        <tr style="background-color: #f2f2f2;">
                            <th style="text-align: left;">Certificate Name/Common NameField</th>
                            <th style="text-align: left;">Type</th>
                            <th style="text-align: left;">Expiry Date</th>
                            <th style="text-align: left;">Owner</th>
                            <th style="text-align: left;">Issued To</th>
                            <th style="text-align: left;">Associated REQ Number</th>
                            <th style="text-align: left;">Days Left/Days Passed</th>
                        </tr>
            
            """

        # Populate table rows with certificate data
        for cert in cert_data:
            html_body += f"""     
                        <tr>
                                <td>{cert.get('Certificate Name', 'N/A') }</td>
                                <td>{cert.get('Type', 'N/A')}</td>
                                <td style="color: red; font-weight: bold;">{cert.get('Expire date', 'N/A')}</td>
                                <td>{cert.get('Owner', 'N/A')}</td>
                                <td>{cert.get('Issued To', 'N/A')}</td>
                                <td>{cert.get('Comment', 'N/A')}</td>"""
            
            # Color coding for Days Until Expiry
            if cert.get("Days Until Expiry") >= 0:
                html_body += f"""<td style="color: red; font-weight: bold; background: yellow;">{cert.get('Days Until Expiry', 'N/A')}</td>"""
            else:
                html_body += f"""<td style="color: yellow; font-weight: bold; background: red;">{cert.get('Days Until Expiry', 'N/A')}</td>"""
            html_body += """</tr>
                            """

        html_body += f"""
                    </table>
            
                    <p>Please prioritize the renewal of"""

        # Check if multiple certificates are present and adjust wording accordingly
        if len(cert_data) > 1:
            html_body += f""" these certificates"""
        else:
            html_body += f""" this certificate"""

        html_body += f""" to ensure continued security and functionality.</p>
            
                    <p>Best regards,<br>
                    <strong>{self.sender_name}</strong><br>
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
            # Create message container
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

            # Send email
            text = msg.as_string()
            server.sendmail(self.email_username, recipient_emails.split(","), text)
            server.quit()

            print(f"Email sent successfully to {recipient_emails}\n")
            return True

        except Exception as e:
            print(f"Failed to send email to {recipient_emails}: {str(e)}")
            return False


# Program entry point
if __name__ == "__main__":
    # Database connection string
    db_connection_string = "Driver={SQL Server};Server=localhost\\SQLEXPRESS;Database=CLM;Trusted_Connection=True"

    load_dotenv()  # Load environment variables from .env file

    # SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_username = "devanshugrwl@gmail.com"
    email_password = os.getenv("Password")  # Use an app password for better security, store it in .env file, and pull the value using os.getenv

    notifier = CertificateExpiryNotifier(
        db_connection_string, smtp_server, smtp_port, email_username, email_password
    )
    notifier.process_expired_certificates()
