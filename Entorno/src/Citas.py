from flask import Blueprint, jsonify, request
from flask import render_template

from conexionFlask import get_db_connection

appC = Blueprint('citas',__name__)


@appC.route('/citas', methods=['GET'])
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

@appC.route('/citas/ver', methods=['GET'])
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


@appC.route('/citas/agendar', methods=['POST'])
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

                # Verificar si ya existe una cita para este paciente en la misma fecha
                cursor.execute("""
                    SELECT ID_Cita FROM Citas WHERE ID_Paciente = ? AND Fecha_Cita = ?
                """, (id_paciente, data['Fecha_Cita']))
                cita_existente = cursor.fetchone()
                if cita_existente:
                    return jsonify({'error': 'El paciente ya tiene una cita para este día.'}), 400

                # Si el paciente existe, se agrega la cita
                cursor.execute("""
                    INSERT INTO Citas (ID_Paciente, Fecha_Cita, Hora_Cita, Descripcion)
                    VALUES (?, ?, ?, ?)
                """, (id_paciente, data['Fecha_Cita'], data['Hora_Cita'], data['Descripcion']))
                connection.commit()

                # Obtenemos el nuevo id
                cita_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]

                # Insertamos la nueva cita en el historial
                cursor.execute("""
                    INSERT INTO Historial (ID_Paciente, ID_Cita, Fecha_Visita, Motivo_Visita)
                    VALUES (?, ?, ?, ?)
                """, (id_paciente, cita_id, data['Fecha_Cita'], data['Descripcion']))

                connection.commit()

                return jsonify({"success": "Cita agendada exitosamente"}), 200
            else:
                # Si el paciente no existe, enviar un error o redirigir
                return jsonify({'error': 'Paciente no encontrado. Favor de registrarlo primero.'}), 404
        except Exception as ex:
            return jsonify({"error": str(ex)}), 500
        finally:
            connection.close()


@appC.route('/citas/cancelar/<int:id_cita>', methods=['PUT'])
def cancelar_cita(id_cita):
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            # Verificar si la cita existe
            cursor.execute("SELECT ID_Paciente, Fecha_Cita, Hora_Cita, Descripcion FROM Citas WHERE ID_Cita = ?", id_cita)
            cita = cursor.fetchone()

            if not cita:
                return jsonify({"error": "Cita no encontrada"}), 404

            # Actualizar el estado de la cita a 'Cancelado'
            cursor.execute("UPDATE Citas SET Estado_Cita = 'Cancelado' WHERE ID_Cita = ?", id_cita)

            connection.close()

            return jsonify({"message": "Cita cancelada"}), 200
        else:
            return jsonify({"error": "Conexión fallida"}), 500