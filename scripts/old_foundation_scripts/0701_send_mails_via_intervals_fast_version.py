
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import smtplib
import pyodbc


def create_email_body(cert_data):
    """Generate an HTML email body for a group of certificates."""
    html_body = f"""
    <html>
        <body>
            <p>Dear Team,</p>
            <p>This is to inform you that the following certificate(s) have <strong>expired or are expiring soon</strong>.</p>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
                <tr style="background-color: #f2f2f2;">
                    <th>Certificate Name</th>
                    <th>Type</th>
                    <th>Expiry Date</th>
                    <th>Owner</th>
                    <th>Issued To</th>
                    <th>Associated REQ</th>
                    <th>Days Left/Passed</th>
                </tr>
    """
    for cert in cert_data:
        days = cert[-1]  # last column = Days Until Expiry
        color = "yellow" if days < 0 else "red"
        bg = "red" if days < 0 else "yellow"
        html_body += f"""
            <tr>
                <td>{cert[0]}</td>
                <td>{cert[5]}</td>
                <td style="color:red; font-weight:bold;">{cert[4]}</td>
                <td>{cert[6]}</td>
                <td>{cert[1]}</td>
                <td>{cert[7]}</td>
                <td style="color:{color}; font-weight:bold; background:{bg};">{days}</td>
            </tr>
        """
    html_body += """
            </table>
            <p>Please take immediate action to renew these certificates.</p>
            <p>Best regards,<br><strong>IT Security Team</strong></p>
        </body>
    </html>
    """
    return html_body


def send_email(recipient_emails, subject, body):
    """Send an HTML email."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = "devanshugrwl@gmail.com"
        msg["To"] = recipient_emails

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            
            load_dotenv() # Ensure environment variables are loaded
            
            server.login("devanshugrwl@gmail.com", os.getenv("Password"))
            server.sendmail("devanshugrwl@gmail.com", recipient_emails.split(','), msg.as_string())

        print(f"✅ Email sent to {recipient_emails}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def process_certificates(batch_size=500):
    """Stream certificates from DB and process them in batches to save memory."""
    conn = pyodbc.connect("Driver={SQL Server};Server=localhost\\SQLEXPRESS;Database=CLM;Trusted_Connection=True")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT [Certificate Name], [Issued To], [Issued By], [Issuing Date], [Expire date], [Type], 
               [Owner], [Comment], DATEDIFF(day, GETDATE(), [Expire date]) AS [Days Until Expiry]
        FROM CLM_Table 
        WHERE DATEDIFF(day, GETDATE(), [Expire date]) < 31 AND [Active] = 'Yes'
    """)

    subject = "!! IMPORTANT !! : Certificate Expiration Notification"

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break

        # Group by (owner, expiry category)
        groups = {}
        for cert in rows:
            owner = cert[6].lower().replace(" ", "")
            issued_to = cert[1].lower().replace(" ", "")
            days = cert[-1]

            if owner == issued_to:
                receivers = owner
            elif owner in issued_to:
                receivers = issued_to
            elif issued_to in owner:
                receivers = owner
            else:
                receivers = owner + "," + issued_to

            # Add expiry category
            if days < 0:
                receivers += "_Expired"
            elif days == 0:
                receivers += "_Today"
            elif days == 7:
                receivers += "_7days"
            elif days == 14:
                receivers += "_14days"
            else:
                receivers += "_30days"

            if receivers not in groups:
                groups[receivers] = []
            groups[receivers].append(cert)

        # Send emails for this batch
        for group, certs in groups.items():
            email_body = create_email_body(certs)
            receivers = group.split("_")[0]  # remove suffix
            send_email(receivers, subject, email_body)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    process_certificates(batch_size=500)
