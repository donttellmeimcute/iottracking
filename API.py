from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Función para obtener una nueva conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="seguridad_7msc1"
    )

# Ruta para mostrar el formulario de inicio de sesión
@app.route('/login_form', methods=['GET'])
def login_form():
    return render_template('login.html')

# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    correo_electronico = datos.get('correo_electronico')
    contraseña = datos.get('contraseña')

    try:
        # Obtener una nueva conexión a la base de datos
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        # Verificar las credenciales del usuario en la base de datos
        consulta = "SELECT * FROM usuarios WHERE correo_electronico = %s AND contraseña = %s"
        valores = (correo_electronico, contraseña)

        cursor.execute(consulta, valores)
        usuario = cursor.fetchone()

        if usuario:
            # Establecer la cookie de autenticación en la respuesta
            response = make_response(jsonify({"mensaje": "Inicio de sesión exitoso"}))
            response.set_cookie('access_token', value=usuario['token'], httponly=True)
            response.set_cookie('correo_electronico', value=correo_electronico)
            return response
        else:
            return jsonify({"mensaje": "Credenciales incorrectas"}), 401

    except Exception as e:
        return jsonify({'error': str(e)})

    finally:
        # Cerrar el cursor y la conexión a la base de datos
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

# Ruta protegida para obtener información de cámaras
@app.route('/camaras', methods=['GET'])
def camaras():
    estado = request.args.get('estado')

    try:
        # Obtener una nueva conexión a la base de datos
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        # Consultar la base de datos para obtener información de las cámaras
        consulta = "SELECT nombre_camara, estado FROM camaras WHERE 1=1"
        if estado:
            consulta += f" AND estado = '{estado}'"

        cursor.execute(consulta)
        resultados = cursor.fetchall()

        camaras_estado = {resultado['nombre_camara']: resultado['estado'] for resultado in resultados}

        return jsonify(camaras_estado), 200

    except Exception as e:
        return jsonify({'error': str(e)})

    finally:
        # Cerrar el cursor y la conexión a la base de datos
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

# Ruta para manejar /logsess
@app.route('/easteregg', methods=['GET'])
def logsess():
    return jsonify({"mensaje": "Huevo de pascua"}), 200

# Ruta para obtener los accesos de un usuario
@app.route('/accesos_usuario/<int:id_usuario>', methods=['GET'])
def accesos_usuario(id_usuario):
    try:
        # Obtener una nueva conexión a la base de datos
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        # Consultar la base de datos para obtener los accesos del usuario
        consulta = "SELECT * FROM accesos WHERE id_usuario = %s"
        valores = (id_usuario,)

        cursor.execute(consulta, valores)
        accesos = cursor.fetchall()

        return jsonify(accesos), 200

    except Exception as e:
        return jsonify({'error': str(e)})

    finally:
        # Cerrar el cursor y la conexión a la base de datos
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

# Ruta para obtener las grabaciones de una cámara
@app.route('/grabaciones_camara/<int:id_camara>', methods=['GET'])
def grabaciones_camara(id_camara):
    try:
        # Obtener una nueva conexión a la base de datos
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        # Consultar la base de datos para obtener las grabaciones de la cámara
        consulta = "SELECT * FROM grabaciones WHERE id_camara = %s"
        valores = (id_camara,)

        cursor.execute(consulta, valores)
        grabaciones = cursor.fetchall()

        return jsonify(grabaciones), 200

    except Exception as e:
        return jsonify({'error': str(e)})

    finally:
        # Cerrar el cursor y la conexión a la base de datos
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

if __name__ == '__main__':
    app.run(debug=True)
