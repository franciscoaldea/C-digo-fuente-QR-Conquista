from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Configuración de conexión
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="QRConquista"
)
cursor = db.cursor(dictionary=True)

# LOGIN

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    nombre_usuario = data.get("nombre_usuario")
    contraseña = data.get("contraseña")

    cursor.execute(
        "SELECT * FROM Usuario WHERE nombre_usuario=%s AND contraseña=%s",
        (nombre_usuario, contraseña)
    )
    user = cursor.fetchone()

    if user:
        return jsonify({"status": "ok", "usuario": user})
    else:
        return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"}), 401

# REGISTRO DE USUARIO
@app.route("/registro", methods=["POST"])
def registro():
    data = request.json
    sql = "INSERT INTO Usuario (nombre_usuario, gmail, contraseña, tipo_usuario) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (data["nombre_usuario"], data["gmail"], data["contraseña"], data["tipo_usuario"]))
    db.commit()
    return jsonify({"status": "ok", "id": cursor.lastrowid})

# LISTAR CURSOS
@app.route("/cursos", methods=["GET"])
def get_cursos():
    cursor.execute("SELECT * FROM Cursos")
    rows = cursor.fetchall()
    return jsonify(rows)

# LISTAR AULAS
@app.route("/aulas", methods=["GET"])
def get_aulas():
    cursor.execute("SELECT * FROM Aulas")
    rows = cursor.fetchall()
    return jsonify(rows)

# DETALLE DE AULA POR ID
@app.route("/aula/<int:id_aula>", methods=["GET"])
def get_aula(id_aula):
    cursor.execute("SELECT * FROM Aulas WHERE id_aula = %s", (id_aula,))
    aula = cursor.fetchone()
    if aula:
        return jsonify(aula)
    else:
        return jsonify({"error": "Aula no encontrada"}), 404

# DETALLE DE CURSO POR ID
@app.route("/curso/<int:id_curso>", methods=["GET"])
def get_curso(id_curso):
    cursor.execute("SELECT * FROM Cursos WHERE id_curso = %s", (id_curso,))
    curso = cursor.fetchone()
    if curso:
        return jsonify(curso)
    else:
        return jsonify({"error": "Curso no encontrado"}), 404
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
