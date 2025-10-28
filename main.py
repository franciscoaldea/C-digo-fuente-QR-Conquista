from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy_garden.zbarcam import ZBarCam
import requests
import qrcode

API_URL = "http://172.29.193.115:5000"


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout principal vertical
        self.layout = MDBoxLayout(
            orientation='vertical',
            spacing=15,
            padding=[20, 20, 20, 30]  # márgenes: izq, arriba, der, abajo
        )

        # ===== Barra superior con botón de login =====
        self.toolbar = MDTopAppBar(
            title="Lector QR",
            left_action_items=[["account", lambda x: self.show_login_dialog()]]
        )
        self.layout.add_widget(self.toolbar)

        # ===== Label de bienvenida / login =====
        self.label = MDLabel(
            text="Iniciá sesión o escaneá un código QR",
            halign="center",
            size_hint_y=None,
            height="40dp"
        )
        self.layout.add_widget(self.label)

        # ===== Lista de aulas (debajo del login) =====
        self.lista_aulas = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None,
            height="200dp",  # fija una altura razonable para que no quede pegado al topbar
        )
        self.layout.add_widget(self.lista_aulas)

        # ===== Espaciador para empujar el botón hacia abajo =====
        self.layout.add_widget(MDLabel(size_hint_y=1))

        # ===== Botón de escaneo (abajo centrado) =====
        btn_scan = MDRaisedButton(
            text="Abrir Cámara y Escanear",
            pos_hint={"center_x": 0.5},
            size_hint=(None, None),
            size=("220dp", "48dp"),
            on_release=self.open_camera
        )
        self.layout.add_widget(btn_scan)

        self.add_widget(self.layout)

        # Variables del login
        self.dialog = None
        self.username = None
        self.password = None
        self.admin_logged = False

        # Cargar aulas al iniciar
        Clock.schedule_once(lambda dt: self.cargar_aulas())

    def open_camera(self, *args):
        self.manager.current = "scanner"

    # =====================================
    # LOGIN ADMIN
    # =====================================
    def show_login_dialog(self):
        if not self.dialog:
            self.username = MDTextField(hint_text="Usuario", required=True)
            self.password = MDTextField(hint_text="Contraseña", password=True, required=True)

            self.dialog = MDDialog(
                title="Iniciar sesión (Admin)",
                type="custom",
                content_cls=MDBoxLayout(
                    self.username,
                    self.password,
                    orientation="vertical",
                    spacing=10,
                    size_hint_y=None,
                    height="120dp",
                ),
                buttons=[
                    MDRaisedButton(
                        text="Cancelar",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="Entrar",
                        on_release=lambda x: self.check_login()
                    ),
                ],
            )
        self.dialog.open()

    def check_login(self):
        data = {
            "nombre_usuario": self.username.text,
            "contraseña": self.password.text
        }

        try:
            response = requests.post(f"{API_URL}/login", json=data)
            if response.status_code == 200:
                user = response.json()
                self.admin_logged = True
                self.dialog.dismiss()
                self.label.text = f"Bienvenido, {user['usuario']['nombre_usuario']}"
                self.cargar_aulas()  # recarga las aulas con botón de editar
            else:
                self.label.text = "Usuario o contraseña incorrectos"
        except Exception as e:
            self.label.text = f"Error de conexión: {e}"

    # =====================================
    # LISTA DE AULAS
    # =====================================
    def cargar_aulas(self):
        """Carga el listado de aulas desde la API (si existe) o fija."""
        self.lista_aulas.clear_widgets()

        try:
            response = requests.get(f"{API_URL}/aulas")
            if response.status_code == 200:
                aulas = response.json()
            else:
                aulas = []
                self.label.text = f"Error al obtener aulas: {response.status_code}"
        except Exception:
            # Si no puede conectar, usa lista de ejemplo
            aulas = [
                {"id": 1, "nombre": "Aula 1 - Laboratorio"},
                {"id": 2, "nombre": "Aula 2 - Informática"},
                {"id": 3, "nombre": "Aula 3 - Electrónica"},
                {"id": 4, "nombre": "Aula 4 - Taller"}
            ]

        for aula in aulas:
            fila = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height="48dp")

            label_aula = MDLabel(text=aula["nombre"], halign="left")
            fila.add_widget(label_aula)

            # Solo muestra "Editar" si el admin está logueado
            if self.admin_logged:
                btn_editar = MDRaisedButton(
                    text="Editar",
                    md_bg_color=(0.2, 0.5, 1, 1),
                    on_release=lambda x, a=aula: self.editar_aula(a)
                )
                fila.add_widget(btn_editar)

            self.lista_aulas.add_widget(fila)

    def editar_aula(self, aula):
        """Abre un diálogo para editar los datos del aula"""
        nombre_field = MDTextField(text=aula["nombre"], hint_text="Nombre del aula")

        dialog = MDDialog(
            title=f"Editar {aula['nombre']}",
            type="custom",
            content_cls=MDBoxLayout(
                nombre_field,
                orientation="vertical",
                spacing=10,
                size_hint_y=None,
                height="80dp",
            ),
            buttons=[
                MDRaisedButton(
                    text="Cancelar",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Guardar",
                    on_release=lambda x: self.guardar_aula(dialog, aula["id"], nombre_field.text)
                ),
            ],
        )
        dialog.open()

    def guardar_aula(self, dialog, aula_id, nuevo_nombre):
        """Ejemplo de guardar aula (envía PUT a la API)."""
        try:
            data = {"nombre": nuevo_nombre}
            response = requests.put(f"{API_URL}/aula/{aula_id}", json=data)
            if response.status_code == 200:
                self.label.text = f"Aula {aula_id} actualizada correctamente"
            else:
                self.label.text = f"Error al actualizar: {response.status_code}"
        except Exception as e:
            self.label.text = f"Error: {e}"
        finally:
            dialog.dismiss()
            self.cargar_aulas()

#  Pantalla de escaneo QR
class ScannerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.zbarcam = ZBarCam()
        layout = MDBoxLayout(orientation="vertical")
        layout.add_widget(self.zbarcam)

        self.label = MDLabel(text="Escaneando...", halign="center", size_hint_y=0.1)
        layout.add_widget(self.label)

        btn_volver = MDRaisedButton(
            text="Volver",
            pos_hint={"center_x": 0.5},
            on_release=self.volver
        )
        layout.add_widget(btn_volver)
        self.add_widget(layout)

        # Verifica cada medio segundo si hay un QR nuevo
        Clock.schedule_interval(self.check_qr, 0.5)

    def check_qr(self, dt):
        if self.zbarcam.symbols:
            qr_data = self.zbarcam.symbols[0].data.decode("utf-8")
            self.label.text = f"Código detectado: {qr_data}"
            self.zbarcam.stop()
            Clock.unschedule(self.check_qr)
            self.handle_qr(qr_data)

    def handle_qr(self, data):
        # Si el QR contiene una URL de la API (por ejemplo: http://172.29.193.115:5000/aula/1)
        if data.startswith("http://") and "/aula/" in data or "/curso/" in data:
            try:
                response = requests.get(data)
                if response.status_code == 200:
                    info = response.json()
                    # Crear texto con los datos de la BBDD
                    texto = "\n".join([f"{k}: {v}" for k, v in info.items()])
                    dialog = MDDialog(
                        title="Datos obtenidos",
                        text=texto,
                        buttons=[
                            MDRaisedButton(
                                text="Cerrar",
                                on_release=lambda x: dialog.dismiss()
                            )
                        ]
                    )
                    dialog.open()
                else:
                    MDDialog(
                        title="Error",
                        text=f"No se pudo obtener información.\nCódigo: {response.status_code}"
                    ).open()
            except Exception as e:
                MDDialog(
                    title="Error de conexión",
                    text=str(e)
                ).open()
        else:
            # Si el QR no tiene formato de enlace de la API
            dialog = MDDialog(title="Código no reconocido", text=f"Contenido: {data}")
            dialog.open()

    def volver(self, *args):
        self.manager.current = "main"
        self.zbarcam.start()
        Clock.schedule_interval(self.check_qr, 0.5)


#  Pantallas de información
class Info1Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(title="Información 1")
        layout.add_widget(toolbar)

        label = MDLabel(
            text="Esta es la información interna del código INFO1.",
            halign="center"
        )
        layout.add_widget(label)

        btn_volver = MDRaisedButton(
            text="Volver al inicio",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.volver()
        )
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def volver(self):
        self.manager.current = "main"


class Info2Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(title="Información 2")
        layout.add_widget(toolbar)

        label = MDLabel(
            text="Esta es la información del código INFO2, con más detalles.",
            halign="center"
        )
        layout.add_widget(label)

        btn_volver = MDRaisedButton(
            text="Volver al inicio",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.volver()
        )
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def volver(self):
        self.manager.current = "main"


#  APP PRINCIPAL
class QRApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(ScannerScreen(name="scanner"))
        sm.add_widget(Info1Screen(name="info1"))
        sm.add_widget(Info2Screen(name="info2"))
        return sm


if __name__ == "__main__":
    QRApp().run()
