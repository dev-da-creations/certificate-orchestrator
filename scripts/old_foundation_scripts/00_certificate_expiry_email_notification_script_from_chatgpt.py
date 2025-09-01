import smtplib
import pyodbc
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re

class CertificateExpiryNotifier:
    def __init__(self, db_connection_string, smtp_server, smtp_port, email_username, email_password):
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
    
    def get_expired_certificates(self):
        """
        Query the database to get expired certificates
        
        Returns:
            List of expired certificate records
        """
        try:
            conn = pyodbc.connect(self.db_connection_string)
            cursor = conn.cursor()
            
            # Query to get expired certificates where Active = 1 (assuming active certificates)
            query = """
            SELECT [SR NO], [Certificate Name], [Issued To], [Issued By], 
                   [Domain], [Issuing Date], [Expire date], [Type], 
                   [Owner], [Owner Contact Details], [Comment], [Issued], [Active]
            FROM certificates 
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
    
    def extract_email_from_contact(self, contact_details):
        """
        Extract email address from contact details string
        
        Args:
            contact_details: String containing contact information
            
        Returns:
            Email address if found, None otherwise
        """
        if not contact_details:
            return None
            
        # Regular expression to find email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, contact_details)
        
        return emails[0] if emails else None
    
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
                    <th style="text-align: left;">Field</th>
                    <th style="text-align: left;">Details</th>
                </tr>
                <tr>
                    <td><strong>Certificate Name/Common Name</strong></td>
                    <td>{cert_data.get('Certificate Name', 'N/A')}</td>
                </tr>
                <tr>
                    <td><strong>Type</strong></td>
                    <td>{cert_data.get('Type', 'N/A')}</td>
                </tr>
                <tr>
                    <td><strong>Expiry Date</strong></td>
                    <td style="color: red; font-weight: bold;">{cert_data.get('Expire date', 'N/A')}</td>
                </tr>
                <tr>
                    <td><strong>Owner</strong></td>
                    <td>{cert_data.get('Owner', 'N/A')}</td>
                </tr>
                <tr>
                    <td><strong>Issued To</strong></td>
                    <td>{cert_data.get('Issued To', 'N/A')}</td>
                </tr>
                <tr>
                    <td><strong>Associated REQ Number</strong></td>
                    <td>{cert_data.get('Comment', 'N/A')}</td>
                </tr>
            </table>
            
            <p>Please prioritize the renewal of this certificate to ensure continued security and functionality.</p>
            
            <p>Best regards,<br>
            <strong>{self.sender_name}</strong><br>
            IT Security Team</p>
        </body>
        </html>
        """
        return html_body
    
    def send_email(self, recipient_email, subject, body):
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
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_username
            msg['To'] = recipient_email
            
            # Add HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Connect to server and send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_username, recipient_email, text)
            server.quit()
            
            print(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {str(e)}")
            return False
    
    def process_expired_certificates(self):
        """
        Main method to process expired certificates and send notifications
        """
        print("Checking for expired certificates...")
        expired_certs = self.get_expired_certificates()
        
        if not expired_certs:
            print("No expired certificates found.")
            return
        
        print(f"Found {len(expired_certs)} expired certificate(s)")
        
        for cert in expired_certs:
            print(f"\nProcessing certificate: {cert.get('Certificate Name')}")
            
            # Create email body
            email_body = self.create_email_body(cert)
            subject = "Certificate Expiration Notification"
            
            # Extract emails from owner contact details
            owner_email = self.extract_email_from_contact(cert.get('Owner'))
            issued_to_email = cert.get('Issued To')  # Assuming this field contains email
            
            # Send to owner if email found
            if owner_email:
                self.send_email(owner_email, subject, email_body)
            else:
                print(f"No valid email found in Owner Contact Details: {cert.get('Owner Contact Details')}")
            
            # Send to issued to person if different from owner
            if issued_to_email and issued_to_email != owner_email:
                # Validate email format
                if re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', issued_to_email):
                    self.send_email(issued_to_email, subject, email_body)
                else:
                    print(f"Invalid email format in 'Issued To' field: {issued_to_email}")

# Example usage
def main():
    # Database connection string using Windows Authentication
    db_connection_string = (
        "Driver={SQL Server};Server=localhost\\SQLEXPRESS;Database=CLM;Trusted_Connection=True"
    )
    
    # Email configuration (modify according to your email provider)
    smtp_server = "smtp.gmail.com"  # or your company's SMTP server
    smtp_port = 587
    email_username = "devanshugrwl@gmail.com"
    email_password = "<REMOVED PASSWORD>"  # Use app password for Gmail
    
    # Create notifier instance
    notifier = CertificateExpiryNotifier(
        db_connection_string, 
        smtp_server, 
        smtp_port, 
        email_username, 
        email_password
    )
    
    # Process expired certificates
    notifier.process_expired_certificates()

if __name__ == "__main__":
    main()