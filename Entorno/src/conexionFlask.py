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
        connection = pyodbc.connect('DRIVER={SQL Server};SERVER=DESKTOP-0TR6RHR;DATABASE=Policlinico;Trusted_Connection=yes;')
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
                'ID': row[0],
                'Nombres': row[1],
                'ApellidoPaterno': row[2],
                'ApellidoMaterno': row[3],
                'DNI': row[4],
                'Genero': row[5],
                'Direccion': row[6],
                'Edad': row[7],
                'Celular': row[8],
                'FechaNacimiento': str(row[9])  # Convertir la fecha a string
            }
            pacientes.append(paciente)
        return jsonify(pacientes)
    else:
        return jsonify({"error": "Conexión fallida"}), 500

    

@app.route('/agregar_paciente', methods=['POST'])
def agregar_paciente():
    data = request.json

    # Verificación de que los datos requeridos existen
    required_fields = ['Nombres', 'ApellidoPaterno', 'ApellidoMaterno','DNI','Genero', 'Direccion', 'Edad', 'Celular', 'FechaNacimiento']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Falta el campo requerido: {field}"}), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Pacientes (Nombres, ApellidoPaterno, ApellidoMaterno, DNI, Genero, Direccion, Edad, 
            Celular, FechaNacimiento) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data['Nombres'], data['ApellidoPaterno'], data['ApellidoMaterno'], data['DNI'],data['Genero'], 
              data['Direccion'], data['Edad'], data['Celular'], 
              data['FechaNacimiento']))
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



if __name__ == '__main__':
    app.run(debug=True)