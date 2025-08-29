import smtplib
import pyodbc

connect_db = pyodbc.connect("Driver={SQL Server};Server=localhost\\SQLEXPRESS;Database=CLM;Trusted_Connection=True")

cursor = connect_db.cursor()

cursor.execute("SELECT [Certificate Name], [Issued To], [Expire Date] FROM CLM_Table WHERE [Expire Date] < GETDATE()")

result = cursor.fetchall()

smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login("devanshugrwl@gmail.com","ppescdlgcuplcygr")

message = "Subject: Certificate Expiry Notification\n\nThe following certificates have expired:\n\n"
for row in result:
				message += f"Certificate Name: {row[0]}, Issued To: {row[1]}, Expire Date: {row[2]}\n"
message += "\nWith Regards,\nDevanshu Agarwal"

smtp.sendmail("devanshugrwl@gmail.com","heredaworks@gmail.com",message)
smtp.quit()