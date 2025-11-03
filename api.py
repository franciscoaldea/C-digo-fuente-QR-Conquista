from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Configuración de conexión
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="QRConquista"
)
cursor = db.cursor(dictionary=True)

# -------------------------------------------------
# LOGIN
# -------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    nombre_usuario = data.get("nombre_usuario")
    contrasena = data.get("contrasena")

    cursor.execute(
        "SELECT * FROM Usuario WHERE nombre_usuario = %s AND contrasena = %s",
        (nombre_usuario, contrasena)
    )
    user = cursor.fetchone()

    if user:
        return jsonify({"status": "ok", "usuario": user})
    else:
        return jsonify({"status": "error", "message": "Usuario o contrasena incorrectos"}), 401


# -------------------------------------------------
# REGISTRO DE USUARIO
# -------------------------------------------------
@app.route("/registro", methods=["POST"])
def registro():
    data = request.json

    # Validar campos obligatorios
    required_fields = ["nombre_usuario", "gmail", "contrasena", "tipo_usuario"]
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"status": "error", "message": "Faltan campos obligatorios"}), 400

    sql = """
        INSERT INTO Usuario (nombre_usuario, gmail, contrasena, tipo_usuario)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (data["nombre_usuario"], data["gmail"], data["contrasena"], data["tipo_usuario"]))
    db.commit()

    return jsonify({"status": "ok", "nombre_usuario": data["nombre_usuario"]})


# -------------------------------------------------
# LISTAR CURSOS
# -------------------------------------------------
@app.route("/cursos", methods=["GET"])
def get_cursos():
    cursor.execute("SELECT * FROM cursos")
    rows = cursor.fetchall()
    return jsonify(rows)


# -------------------------------------------------
# LISTAR AULAS
# -------------------------------------------------
@app.route("/aulas", methods=["GET"])
def get_aulas():
    cursor.execute("SELECT * FROM aulas")
    rows = cursor.fetchall()
    return jsonify(rows)


# -------------------------------------------------
# DETALLE DE AULA POR ID
# -------------------------------------------------
@app.route("/aula/<int:id_aula>", methods=["GET"])
def get_aula(id_aula):
    cursor.execute("SELECT * FROM aulas WHERE id_aula = %s", (id_aula,))
    aula = cursor.fetchone()
    if aula:
        return jsonify(aula)
    else:
        return jsonify({"error": "Aula no encontrada"}), 404


# -------------------------------------------------
# DETALLE DE CURSO POR ID
# -------------------------------------------------
@app.route("/curso/<int:id_curso>", methods=["GET"])
def get_curso(id_curso):
    cursor.execute("SELECT * FROM cursos WHERE id_curso = %s", (id_curso,))
    curso = cursor.fetchone()
    if curso:
        return jsonify(curso)
    else:
        return jsonify({"error": "Curso no encontrado"}), 404


# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
