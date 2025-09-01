import pyodbc

connect_db = pyodbc.connect("Driver={SQL Server};Server=localhost\\SQLEXPRESS;Database=CLM;Trusted_Connection=True")

cursor = connect_db.cursor()

cursor.execute("SELECT [Certificate Name], [Issued To], [Expire Date] FROM CLM_Table WHERE [Expire Date] < GETDATE()")

result = cursor.fetchall()

# Prints all result
print("Prints all results - \n")

for row in result:
				print(f"Certificate Name: {row[0]}, Issued To: {row[1]}, Expire Date: {row[2]}")

# Prints only first 2 result
print("\n\nPrints only first 2 results - \n")

i = len(result)

for row in result:
				if len(result)-i < 2:
								print(f"Certificate Name: {row[0]}, Issued To: {row[1]}, Expire Date: {row[2]}")
				i -= 1

# Prints only last 2 result
print("\n\nPrints only last 2 results - \n")

i = len(result)

for row in result:
				if i <= 2:	
								print(f"Certificate Name: {row[0]}, Issued To: {row[1]}, Expire Date: {row[2]}")
				i -= 1