import pyodbc

try:
    connection=pyodbc.connect('DRIVER={SQL Server};SERVER=DESKTOP-0TR6RHR;DATABASE=Policlinico;Trusted_Connection=yes;')
    print("Conexión exitosa")

    cursor= connection.cursor()
    #cursor.execute("SELECT @@version;")
    #row=cursor.fetchone()
    #print(row)

    cursor.execute("SELECT * FROM Pacientes;")
    rows=cursor.fetchall()
    for row in rows:
        print(row)

except Exception as ex:
    print(ex)
finally:
    connection.close()
    print("Conexión finalizada")