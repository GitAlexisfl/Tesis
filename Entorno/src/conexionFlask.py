import pyodbc
from flask import Flask, jsonify
from flask import request, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)

TOKEN = 'apis-token-10581.LsKb-aYQ4BCNiCTETgfVGaGv5u8aHk-G'

CORS(app)

def get_db_connection():
    try:
        connection_string = ('DRIVER={SQL Server};SERVER=DESKTOP-0TR6RHR;DATABASE=Policlinico;Trusted_Connection=yes;')
        connection = pyodbc.connect(connection_string, autocommit=True, pooling=True)
        return connection
    except Exception as ex:
        print(ex)
        return None

@app.route('/pacientes', methods=['GET'])
def get_pacientes():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Pacientes;")
        rows = cursor.fetchall()
        connection.close()

        # Verificar qué datos se están enviando a la respuesta
        print(rows)  # Agrega esto para depuración

        pacientes = []
        for row in rows:
            paciente = {
                'ID_Paciente': row[0],
                'Nombre': row[1],
                'Apellido_Paterno': row[2],
                'Apellido_Materno': row[3],
                'DNI': row[4],
                'Genero': row[5],
                'Direccion': row[6],
                'Edad': row[7],
                'Celular': row[8],
                'Fecha_Nacimiento': str(row[9])  # Convertir la fecha a string
            }
            pacientes.append(paciente)
        return jsonify(pacientes)
    else:
        return jsonify({"error": "Conexión fallida"}), 500

    

@app.route('/agregar_paciente', methods=['POST'])
def agregar_paciente():
    data = request.json

    # Verificación de que los datos requeridos existen
    required_fields = ['Nombre', 'Apellido_Paterno', 'Apellido_Materno','DNI','Genero', 'Direccion', 'Edad', 'Celular', 'Fecha_Nacimiento']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Falta el campo requerido: {field}"}), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Pacientes (Nombre, Apellido_Paterno, Apellido_Materno, DNI, Genero, Direccion, Edad, 
            Celular, Fecha_Nacimiento) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data['Nombre'], data['Apellido_Paterno'], data['Apellido_Materno'], data['DNI'],data['Genero'], 
              data['Direccion'], data['Edad'], data['Celular'], 
              data['Fecha_Nacimiento']))
        connection.commit()
        return jsonify({"success": "Paciente agregado exitosamente"}), 200
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500
    finally:
        connection.close()



@app.route('/pacientes/buscar', methods=['POST'])
def buscar_dni():
    dni = request.form.get('dni')

    url = f'https://api.apis.net.pe/v2/reniec/dni?numero={dni}'

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Esto lanzará un error si la respuesta no es 200
        data = response.json()  # Obtener los datos en formato JSON

        return jsonify(data)  # Asegurarse de que se devuelve un JSON
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'HTTP error occurred: {http_err}'}), 500
    except Exception as err:
        return jsonify({'error': f'An error occurred: {err}'}), 500

@app.route('/pacientes/buscarBD', methods=['POST'])
def buscar_paciente_bd():
    dni = request.form.get('dni')  # Get DNI from form input

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        # Query for patient by DNI
        cursor.execute("SELECT * FROM Pacientes WHERE DNI = ?", dni)
        row = cursor.fetchone()
        connection.close()

        if row:
            paciente = {
                'ID_Paciente': row[0],
                'Nombre': row[1],
                'Apellido_Paterno': row[2],
                'Apellido_Materno': row[3],
                'DNI': row[4],
                'Genero': row[5],
                'Direccion': row[6],
                'Edad': row[7],
                'Celular': row[8],
                'Fecha_Nacimiento': str(row[9])
            }
            return jsonify(paciente)
        else:
            return jsonify({'error': 'Paciente no encontrado'}), 404
    else:
        return jsonify({"error": "Conexión fallida"}), 500
    


@app.route('/citas', methods=['GET'])
def get_citas():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Citas;")
        rows = cursor.fetchall()
        connection.close()

        # Verificar qué datos se están enviando a la respuesta
        print(rows)  # Agrega esto para depuración

        citas = []
        for row in rows:
            cita = {
                'ID_Cita': row[0],
                'ID_Paciente': row[1],
                'Fecha_Cita': str(row[2]), # Convertir la fecha a string
                'Hora_Cita': row[3],
                'Descripcion': row[4]                                
            }
            citas.append(cita)
        return jsonify(citas)
    else:
        return jsonify({"error": "Conexión fallida"}), 500
    

# View appointments for a specific date
@app.route('/citas/ver', methods=['GET'])
def ver_citas():
    fecha_cita = request.args.get('fecha')  # Obtain the date from the request (format: YYYY-MM-DD)

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        # Query to get all appointments for the given date
        cursor.execute("""
            SELECT c.ID_Cita, p.Nombre, p.Apellido_Paterno, p.Apellido_Materno, c.Fecha_Cita, c.Hora_Cita, c.Descripcion
            FROM Citas c
            JOIN Pacientes p ON c.ID_Paciente = p.ID_Paciente
            WHERE c.Fecha_Cita = ?
        """, fecha_cita)
        rows = cursor.fetchall()
        connection.close()

        citas = []
        for row in rows:
            cita = {
                'ID_Cita': row[0],
                'Nombre': row[1],
                'Apellido_Paterno': row[2],
                'Apellido_Materno': row[3],
                'Fecha_Cita': str(row[4]),
                'Hora_Cita': str(row[5]),
                'Descripcion': row[6]
            }
            citas.append(cita)

        if citas:
            return jsonify(citas)
        else:
            return jsonify({'message': 'No hay citas para la fecha seleccionada'}), 404
    else:
        return jsonify({"error": "Conexión fallida"}), 500


@app.route('/citas/agendar', methods=['POST'])
def agendar_cita():
    data = request.json

    # Verificación de que los datos requeridos existen
    required_fields = ['DNI', 'Fecha_Cita', 'Hora_Cita', 'Descripcion']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Falta el campo requerido: {field}"}), 400

    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Conexión fallida"}), 500
        
        cursor = connection.cursor()

        # Buscar el paciente por DNI
        cursor.execute("SELECT ID_Paciente FROM Pacientes WHERE DNI = ?", data['DNI'])
        paciente = cursor.fetchone()

        if paciente:
            id_paciente = paciente[0]
            # Si el paciente existe, se agrega la cita
            cursor.execute("""
                INSERT INTO Citas (ID_Paciente, Fecha_Cita, Hora_Cita, Descripcion)
                VALUES (?, ?, ?, ?)
            """, (id_paciente, data['Fecha_Cita'], data['Hora_Cita'], data['Descripcion']))
            connection.commit()
            return jsonify({"success": "Cita agendada exitosamente"}), 200
        else:
            # Si el paciente no existe, enviar un error o redirigir
            return jsonify({'error': 'Paciente no encontrado. Favor de registrarlo primero.'}), 404
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500
    finally:
        connection.close()



if __name__ == '__main__':
    app.run(debug=True)