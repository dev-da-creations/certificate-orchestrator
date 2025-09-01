import pyodbc

connect_db = pyodbc.connect("Driver={SQL Server};Server=localhost\\SQLEXPRESS;Database=CLM;Trusted_Connection=True")

cursor = connect_db.cursor()

cursor.execute("SELECT [Certificate Name], [Issued To], [Expire Date] FROM CLM_Table WHERE [Expire Date] < GETDATE()")

result = cursor.fetchall()

print(result)