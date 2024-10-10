from flask import Blueprint, jsonify, request
from flask import render_template
import requests
from conexionFlask import get_db_connection

appP = Blueprint('pacientes',__name__)

TOKEN = 'apis-token-10581.LsKb-aYQ4BCNiCTETgfVGaGv5u8aHk-G'


@appP.route('/pacientes', methods=['GET'])
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

    

@appP.route('/agregar_paciente', methods=['POST'])
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
            #registrar paciente
            cursor.execute("""
                INSERT INTO Pacientes (Nombre, Apellido_Paterno, Apellido_Materno, DNI, Genero, Direccion, Edad, 
                Celular, Fecha_Nacimiento) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data['Nombre'], data['Apellido_Paterno'], data['Apellido_Materno'], data['DNI'],data['Genero'], 
                data['Direccion'], data['Edad'], data['Celular'], 
                data['Fecha_Nacimiento']))
            
            #Obtener el ID del paciente recien registradp
            connection.commit()
            id_paciente = cursor.execute("SELECT @@IDENTITY").fetchone()[0]

            # Crear el historial asociado al paciente
            cursor.execute("""
                INSERT INTO Historial (ID_Paciente, ID_Cita, Fecha_Visita, Motivo_Visita)
                VALUES (?, NULL, NULL, 'Historial creado para nuevo paciente')
            """, id_paciente)
            connection.commit()

            return jsonify({"success": "Paciente agregado exitosamente"}), 200
        except Exception as ex:
            return jsonify({"error": str(ex)}), 500
        finally:
            connection.close()



@appP.route('/pacientes/buscar', methods=['POST'])
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

@appP.route('/pacientes/buscarBD', methods=['POST'])
def buscar_paciente_bd():
        dni = request.form.get('dni')  # Get DNI from form input
        nombre = request.form.get('nombre')

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
        
@appP.route('/pacientes/buscarND', methods=['POST'])
def buscar_paciente_nd():
    busqueda = request.json.get('busqueda')  # Obtener lo que el usuario ingresó

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()

        # Puedes usar ese valor para buscar en DNI, nombre, apellido paterno o apellido materno
        query = "SELECT * FROM Pacientes WHERE DNI = ? OR Nombre LIKE ? OR Apellido_Paterno LIKE ? OR Apellido_Materno LIKE ?"
        params = [busqueda, f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%']

        # Si no se proporcionó ningún campo, devolver un error
        if not params:
            return jsonify({"error": "Debes proporcionar DNI, Nombre, Apellido Paterno o Apellido Materno"}), 400

        # Ejecutar la consulta con los parámetros
        cursor.execute(query, params)
        rows = cursor.fetchall()
        connection.close()

        if rows:
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
                    'Fecha_Nacimiento': str(row[9])
                }
                pacientes.append(paciente)
            return jsonify(pacientes), 200
        else:
            return jsonify({'error': 'Paciente(s) no encontrado(s)'}), 404
    else:
        return jsonify({"error": "Conexión fallida"}), 500
    
@appP.route('/pacientes/actualizar/<int:id_paciente>', methods=['PUT'])
def actualizar_paciente(id_paciente):
    data = request.json  # Obtener los datos enviados en el cuerpo de la solicitud

    # Verificación de que los campos requeridos están presentes en la solicitud
    required_fields = ['Nombre', 'Apellido_Paterno', 'Apellido_Materno', 'DNI', 'Genero', 'Direccion', 'Edad', 'Celular', 'Fecha_Nacimiento']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Falta el campo requerido: {field}"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Actualizar los datos del paciente en la base de datos
        cursor.execute("""
            UPDATE Pacientes 
            SET Nombre = ?, Apellido_Paterno = ?, Apellido_Materno = ?, DNI = ?, Genero = ?, Direccion = ?, Edad = ?, Celular = ?, Fecha_Nacimiento = ?
            WHERE ID_Paciente = ?
        """, (
            data['Nombre'], 
            data['Apellido_Paterno'], 
            data['Apellido_Materno'], 
            data['DNI'], 
            data['Genero'], 
            data['Direccion'], 
            data['Edad'], 
            data['Celular'], 
            data['Fecha_Nacimiento'], 
            id_paciente
        ))

        connection.commit()  # Confirmar los cambios en la base de datos
        return jsonify({"success": "Paciente actualizado exitosamente"}), 200
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500
    finally:
        connection.close()
