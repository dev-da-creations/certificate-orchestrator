from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import pyodbc

# Database connection
connect_db = pyodbc.connect("Driver={SQL Server};Server=localhost\\SQLEXPRESS;Database=CLM;Trusted_Connection=True")
cursor = connect_db.cursor()
cursor.execute("SELECT [Certificate Name], [Issued To], [Expire Date] FROM CLM_Table WHERE [Expire Date] < GETDATE()")
result = cursor.fetchall()
cursor.execute("SELECT * FROM CLM_Table WHERE [Expire Date] < GETDATE()")
result_data = cursor.fetchall()

# SMTP setup
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login("devanshugrwl@gmail.com", "<REMOVED PASSWORD>")

sender_email = "devanshugrwl@gmail.com"
receiver_email = []
subject = "Certificate Expiry Notification"

# Collect receiver emails
for row in result:
    receiver_email.append(row[1])  # Assuming 'Issued To' is the email address

# Send emails
for i in range(len(result)):
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["Subject"] = subject
    message["To"] = receiver_email[i]
    
    plain_text_content = "This is the plain text version of the email."
    
    html_content = f"""
    <html>
        <body>
            <p>Dear {receiver_email[i]},</p>
            <p>The following certificate has expired on {result[i][2]}:</p>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
                <tr style="background-color: #f2f2f2;">
                    <th style="text-align: left;">Field</th>
                    <th style="text-align: left;">Details</th>
                </tr>
                <tr>
                    <td><strong>Certificate Name/Common Name</strong></td>
                    <td>{result_data[i][1]}</td>
                </tr>
                <tr>
                    <td><strong>Type</strong></td>
                    <td>{result_data[i][7]}</td>
                </tr>
                <tr>
                    <td><strong>Expiry Date</strong></td>
                    <td style="color: red; font-weight: bold;">{result_data[i][6]}</td>
                </tr>
                <tr>
                    <td><strong>Owner</strong></td>
                    <td>{result_data[i][8]}</td>
                </tr>
                <tr>
                    <td><strong>Issued To</strong></td>
                    <td>{result_data[i][2]}</td>
                </tr>
                <tr>
                    <td><strong>Associated REQ Number</strong></td>
                    <td>{result_data[i][10]}</td>
                </tr>
            </table>
            
            <p>Please prioritize the renewal of this certificate to ensure continued security and functionality.</p>
            
            <p>Best regards,<br>
            <strong>Devanshu Agarwal</strong><br>
            IT Security Team</p>
        </body>
    </html>
    """
    
    part1 = MIMEText(plain_text_content, "plain")
    part2 = MIMEText(html_content, "html")
    message.attach(part1)
    message.attach(part2)
    
    smtp.sendmail(sender_email, receiver_email[i], message.as_string())
    print(f"Email sent to {receiver_email[i]} regarding certificate {result[i][0]} expiry.")

smtp.quit()
connect_db.close()