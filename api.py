from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# --- CONEXIÓN BASE DE DATOS ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="QRConquista"
)
cursor = db.cursor(dictionary=True)

# --- LOGIN ---
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    nombre_usuario = data.get("nombre_usuario")
    contraseña = data.get("contraseña")

    if not nombre_usuario or not contraseña:
        return jsonify({"status": "error", "message": "Faltan datos"}), 400

    cursor.execute(
        "SELECT * FROM Usuario WHERE nombre_usuario = %s AND contraseña = %s",
        (nombre_usuario, contraseña)
    )
    user = cursor.fetchone()

    if user:
        return jsonify({"status": "ok", "usuario": user})
    else:
        return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"}), 401


# --- REGISTRO ---
@app.route("/registro", methods=["POST"])
def registro():
    data = request.json
    required_fields = ["nombre_usuario", "gmail", "contraseña", "tipo_usuario"]
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"status": "error", "message": "Faltan campos"}), 400

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
    db.commit()

    return jsonify({"status": "ok", "nombre_usuario": data["nombre_usuario"]})


# --- LISTAR AULAS ---
@app.route("/aulas", methods=["GET"])
def get_aulas():
    cursor.execute("SELECT * FROM aulas")
    rows = cursor.fetchall()
    return jsonify(rows)


# --- OBTENER DETALLE DE AULA ---
@app.route("/aula/<int:id_aula>", methods=["GET"])
def get_aula(id_aula):
    cursor.execute("SELECT * FROM aulas WHERE id_aula = %s", (id_aula,))
    aula = cursor.fetchone()
    if aula:
        return jsonify(aula)
    else:
        return jsonify({"error": "Aula no encontrada"}), 404


# --- EDITAR AULA COMPLETA ---
@app.route("/aula/<int:id_aula>", methods=["PUT"])
def editar_aula(id_aula):
    data = request.json
    nombre = data.get("nombre")
    curso = data.get("curso")
    estado = data.get("estado")
    especialidad = data.get("especialidad")

    if not nombre or not curso or not estado or not especialidad:
        return jsonify({"error": "Faltan datos del aula"}), 400

    sql = """
        UPDATE aulas
        SET nombre = %s, curso = %s, estado = %s, especialidad = %s
        WHERE id_aula = %s
    """
    cursor.execute(sql, (nombre, curso, estado, especialidad, id_aula))
    db.commit()

    return jsonify({"status": "ok", "message": "Aula actualizada correctamente"})


# --- LISTAR CURSOS ---
@app.route("/cursos", methods=["GET"])
def get_cursos():
    cursor.execute("SELECT * FROM cursos")
    rows = cursor.fetchall()
    return jsonify(rows)


# --- DETALLE DE CURSO ---
@app.route("/curso/<int:id_curso>", methods=["GET"])
def get_curso(id_curso):
    cursor.execute("SELECT * FROM cursos WHERE id_curso = %s", (id_curso,))
    curso = cursor.fetchone()
    if curso:
        return jsonify(curso)
    else:
        return jsonify({"error": "Curso no encontrado"}), 404


# --- MAIN ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
