import pyodbc

def get_db_connection():
    try:
        connection_string = ('DRIVER={SQL Server};SERVER=DESKTOP-0TR6RHR;DATABASE=Policlinico;Trusted_Connection=yes;')
        connection = pyodbc.connect(connection_string, autocommit=True, pooling=True)
        return connection
    except Exception as ex:
        print(ex)
        return None




