import qrcode
import os

directorio = os.path.dirname(os.path.abspath(__file__))

API_IP = "172.29.193.115"  # tu IP de WSL
aula_id = 1
url = f"http://{API_IP}:5000/aula/{aula_id}"

img = qrcode.make(url)

# Ruta completa del archivo
ruta_qr = os.path.join(directorio, f"qr_aula{aula_id}.png")
img.save(ruta_qr)

print(f"✅ QR generado en: {ruta_qr}")
