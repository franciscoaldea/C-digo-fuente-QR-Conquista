from flask import Flask, request, jsonify
import mysql.connector


app = Flask(__name__)


# Configuración de conexión
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="123456",
    database="QRConquista"
)
cursor = db.cursor(dictionary=True)


# ======================
# LOGIN
# ======================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    gmail = data.get("gmail")
    contraseña = data.get("contraseña")


    cursor.execute("SELECT * FROM Usuario WHERE gmail=%s AND contraseña=%s", (gmail, contraseña))
    user = cursor.fetchone()


    if user:
        return jsonify({"status": "ok", "usuario": user})
    else:
        return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401


# ======================
# REGISTRO DE USUARIO
# ======================
@app.route("/registro", methods=["POST"])
def registro():
    data = request.json
    sql = "INSERT INTO Usuario (nombre_usuario, gmail, contraseña, tipo_usuario) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (data["nombre_usuario"], data["gmail"], data["contraseña"], data["tipo_usuario"]))
    db.commit()
    return jsonify({"status": "ok", "id": cursor.lastrowid})


# ======================
# LISTAR CURSOS
# ======================
@app.route("/cursos", methods=["GET"])
def get_cursos():
    cursor.execute("SELECT * FROM Cursos")
    rows = cursor.fetchall()
    return jsonify(rows)


# ======================
# LISTAR AULAS
# ======================
@app.route("/aulas", methods=["GET"])
def get_aulas():
    cursor.execute("SELECT * FROM Aulas")
    rows = cursor.fetchall()
    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



