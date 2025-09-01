from unittest import result
import pyodbc

connect_db = pyodbc.connect("Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=CLM;Trusted_Connection=True")

cursor = connect_db.cursor()
cursor.execute("SELECT * FROM CLM_Table")

result	= cursor.fetchall()

print(result)