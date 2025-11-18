# IMPORTACIONES
from flask import Flask, request, jsonify  # Flask para la API, request para recibir datos, jsonify para enviar JSON
import mysql.connector                    # Conector para MySQL

# CONFIGURACIÓN DE LA APP
app = Flask(__name__)  # Inicializa la aplicación Flask

# CONEXIÓN A BASE DE DATOS
db = mysql.connector.connect(
    host="localhost",      # Servidor de base de datos
    user="root",           # Usuario de la base
    password="123456",     # Contraseña del usuario
    database="QRConquista" # Base de datos a usar
)
cursor = db.cursor(dictionary=True)  # Cursor que devuelve resultados como diccionarios

# RUTAS DE LA API

#LOGIN
@app.route("/login", methods=["POST"])
def login():
    """Verifica credenciales del usuario y retorna información si son correctas."""
    data = request.json  # Datos enviados en formato JSON
    nombre_usuario = data.get("nombre_usuario")  # Obtiene usuario
    contraseña = data.get("contraseña")         # Obtiene contraseña

    # Validación de campos vacíos
    if not nombre_usuario or not contraseña:
        return jsonify({"status": "error", "message": "Faltan datos"}), 400

    # Consulta en la base de datos
    cursor.execute(
        "SELECT * FROM Usuario WHERE nombre_usuario = %s AND contraseña = %s",
        (nombre_usuario, contraseña)
    )
    user = cursor.fetchone()  # Obtiene la primera coincidencia

    if user:
        return jsonify({"status": "ok", "usuario": user})  # Login exitoso
    else:
        return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"}), 401

#REGISTRO
@app.route("/registro", methods=["POST"])
def registro():
    """Registra un nuevo usuario en la base de datos."""
    data = request.json
    required_fields = ["nombre_usuario", "gmail", "contraseña", "tipo_usuario"]

    # Validación de campos obligatorios
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"status": "error", "message": "Faltan campos"}), 400

    # Inserción en la base de datos
    sql = """
        INSERT INTO Usuario (nombre_usuario, gmail, contraseña, tipo_usuario)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (
        data["nombre_usuario"],
        data["gmail"],
        data["contraseña"],
        data["tipo_usuario"]
    ))
    db.commit()  # Confirma los cambios

    return jsonify({"status": "ok", "nombre_usuario": data["nombre_usuario"]})

#LISTADO DE AULAS
@app.route("/aulas", methods=["GET"])
def get_aulas():
    """Devuelve la lista de todas las aulas."""
    cursor.execute("SELECT * FROM vista_aulas")
    rows = cursor.fetchall()  # Obtiene todos los registros
    return jsonify(rows)

# DETALLE DE UNA AULA (incluye turno)
@app.route("/aula/<int:id>", methods=["GET"])
def get_aula(id):
    sql = """
        SELECT 
            a.id_aula AS id,
            a.nombre,
            a.curso,
            a.estado,
            a.especialidad,
            c.Turno AS turno
        FROM Aulas a
        LEFT JOIN Cursos c ON a.id_aula = c.fk_aula
        WHERE a.id_aula = %s
        LIMIT 1
    """
    cursor.execute(sql, (id,))
    aula = cursor.fetchone()
    if aula:
        return jsonify(aula)
    else:
        return jsonify({"error": "Aula no encontrada"}), 404

# EDITAR AULA (incluye actualización de turno)
@app.route("/aula/<int:id_aula>", methods=["PUT"])
def editar_aula(id_aula):
    data = request.json
    nombre = data.get("nombre")
    curso = data.get("curso")
    estado = data.get("estado")
    especialidad = data.get("especialidad")
    turno = data.get("turno")  # NUEVO

    if not nombre or not curso or not estado or not especialidad or not turno:
        return jsonify({"error": "Faltan datos del aula"}), 400

    # Actualizar Aulas
    sql_aula = """
        UPDATE Aulas
        SET nombre = %s, curso = %s, estado = %s, especialidad = %s
        WHERE id_aula = %s
    """
    cursor.execute(sql_aula, (nombre, curso, estado, especialidad, id_aula))

    # Actualizar Turno en Cursos
    sql_curso = """
        UPDATE Cursos
        SET Turno = %s
        WHERE fk_aula = %s
    """
    cursor.execute(sql_curso, (turno, id_aula))

    db.commit()
    return jsonify({"status": "ok", "message": "Aula y turno actualizados correctamente"})

#LISTADO DE CURSOS
@app.route("/cursos", methods=["GET"])
def get_cursos():
    """Devuelve todos los cursos."""
    cursor.execute("SELECT * FROM Cursos")
    rows = cursor.fetchall()
    return jsonify(rows)

#DETALLE DE UN CURSO
@app.route("/curso/<int:id_curso>", methods=["GET"])
def get_curso(id_curso):
    """Devuelve información de un curso específico."""
    cursor.execute("SELECT * FROM Cursos WHERE id_curso = %s", (id_curso,))
    curso = cursor.fetchone()
    if curso:
        return jsonify(curso)
    else:
        return jsonify({"error": "Curso no encontrado"}), 404


# EJECUCIÓN DE LA APP
if __name__ == "__main__":
    # Ejecuta la app en modo debug, accesible desde cualquier IP local
    app.run(host="0.0.0.0", port=5000, debug=True)
