import requests
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy_garden.zbarcam import ZBarCam
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivymd.uix.card import MDCard
from kivymd.utils.set_bars_colors import set_bars_colors

# Constantes
API_URL = "http://localhost:5000"
OPCIONES_ESTADO = ["Libre", "Ocupada", "Cerrada"]


# =====================================
# CLASE DE VISTA PRINCIPAL
# Se reduce el __init__ delegando la UI al .kv
# =====================================
class MainScreen(Screen):
    # Nota: Los widgets como 'main_label' y 'aulas_container'
    # son ahora IDs definidos en qr_app.kv
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog_login = None
        self.dialog_editar = None
        self.menu_estado = None
        self.admin_logged = False
        self.aulas = []

    # Se llama cuando la pantalla está a punto de ser mostrada
    def on_pre_enter(self):
        # Opcional: Establecer un color de fondo para la barra de estado si KivyMD lo soporta
        # set_bars_colors(self.theme_cls.primary_color, self.theme_cls.primary_color)
        pass

    # =====================================
    # LÓGICA DE LOGIN (MÉTODOS PRIVADOS RECOMENDADOS)
    # =====================================
    def show_login_dialog(self):
        # Mantiene la lógica de creación de diálogos
        if not self.dialog_login:
            # Los campos se definen en el .kv, aquí se instancian si no existen
            self.username_field = MDTextField(hint_text="Usuario", required=True)
            self.password_field = MDTextField(hint_text="Contraseña", password=True, required=True)

            content_box = MDBoxLayout(
                self.username_field,
                self.password_field,
                orientation="vertical",
                spacing="10dp",
                size_hint_y=None,
                height="120dp",
            )
            
            self.dialog_login = MDDialog(
                title="Iniciar sesión (Admin)",
                type="custom",
                content_cls=content_box,
                buttons=[
                    MDRaisedButton(text="Cancelar", on_release=lambda x: self.dialog_login.dismiss()),
                    MDRaisedButton(text="Entrar", on_release=lambda x: self._check_login()),
                ],
            )
        self.dialog_login.open()

    def _check_login(self):
        # Implementación de la funcionalidad sin cambios, se renombra a _check_login
        data = {
            "nombre_usuario": self.username_field.text,
            "contraseña": self.password_field.text
        }

        try:
            response = requests.post(f"{API_URL}/login", json=data)
            main_label = self.ids.main_label
            aulas_container = self.ids.aulas_container
            
            if response.status_code == 200:
                user = response.json()
                self.admin_logged = True
                self.dialog_login.dismiss()
                main_label.text = f"Bienvenido, {user['usuario']['nombre_usuario']}"
                aulas_container.opacity = 1
                aulas_container.disabled = False
                self.cargar_aulas()
            else:
                main_label.text = "Usuario o contraseña incorrectos"
        except Exception as e:
            self.ids.main_label.text = f"Error de conexión: {e}"

    # =====================================
    # LÓGICA DE AULAS
    # =====================================
    def cargar_aulas(self):
        # Renombrado y uso de IDs del .kv
        aulas_container = self.ids.aulas_container
        aulas_container.clear_widgets()

        try:
            response = requests.get(f"{API_URL}/aulas")
            if response.status_code == 200:
                self.aulas = response.json()
            else:
                self.aulas = []
                self.ids.main_label.text = f"Error al obtener aulas: {response.status_code}"
        except Exception:
            # Datos de simulación para fallback
            self.aulas = [
                {"id": 1, "nombre": "Aula 1", "curso": "3°A", "estado": "Libre", "especialidad": "Computación"},
                {"id": 2, "nombre": "Aula 2", "curso": "4°B", "estado": "Ocupada", "especialidad": "Computación"},
                {"id": 3, "nombre": "Aula 3", "curso": "5°A", "estado": "Cerrada", "especialidad": "Computación"},
                {"id": 4, "nombre": "Aula 4", "curso": "6°A", "estado": "Libre", "especialidad": "Computación"},
            ]

        for aula in self.aulas:
            self.mostrar_aula(aula)

    def mostrar_aula(self, aula):
        """Crea una tarjeta con los datos del aula (mejorado con MDListItem)"""
        
        # Mapeo de estado a ícono (Mejora visual)
        iconos = {"Libre": "check-circle", "Ocupada": "alert-circle", "Cerrada": "close-circle"}
        color_estado = {"Libre": (0, 0.6, 0, 1), "Ocupada": (0.8, 0.4, 0, 1), "Cerrada": (0.6, 0, 0, 1)}
        estado = aula.get('estado', 'Cerrada')
        
        # Uso de MDCard y OneLineIconListItem para un diseño más pulido
        card = MDCard(
            orientation="vertical", 
            padding="10dp", 
            spacing="10dp",
            size_hint_y=None, 
            height="100dp", 
            ripple_behavior=True, # Retroalimentación visual al tocar
        )

        # Contenedor del contenido (más limpio que un MDLabel gigante)
        content_layout = MDBoxLayout(orientation='horizontal', padding="5dp", spacing="10dp")

        # Icono con color basado en el estado
        icon_widget = IconLeftWidget(
            icon=iconos.get(estado, "help-circle"),
            theme_text_color="Custom",
            text_color=color_estado.get(estado, (0.5, 0.5, 0.5, 1))
        )
        content_layout.add_widget(icon_widget)

        # Información detallada
        info_label = MDLabel(
            text=f"[b]{aula['nombre']}[/b] ([color={self._get_hex_color(color_estado.get(estado))}]{estado}[/color])\n"
                 f"Curso: {aula.get('curso', '-')}\n"
                 f"Especialidad: {aula.get('especialidad', 'Computación')}",
            markup=True,
            halign="left",
            valign="center",
            font_style="Body2"
        )
        content_layout.add_widget(info_label)
        
        card.add_widget(content_layout)

        if self.admin_logged:
            btn_editar = MDRaisedButton(
                text="Editar",
                size_hint_y=None, 
                height="36dp",
                pos_hint={"center_x": 0.5},
                on_release=lambda x, a=aula: self._editar_aula(a)
            )
            card.add_widget(btn_editar)

        self.ids.aulas_container.add_widget(card)

    def _get_hex_color(self, rgba):
        """Convierte (r, g, b, a) a formato hexadecimal #RRGGBB"""
        if not rgba or len(rgba) < 3: return "#808080" # Gris por defecto
        return f"#{int(rgba[0]*255):02x}{int(rgba[1]*255):02x}{int(rgba[2]*255):02x}"

    # =====================================
    # LÓGICA DE EDICIÓN
    # =====================================
    def _editar_aula(self, aula):
        # Separación de creación de widgets y el diálogo
        self.nombre_field = MDTextField(text=aula.get("nombre", ""), hint_text="Nombre del aula")
        self.curso_field = MDTextField(text=aula.get("curso", ""), hint_text="Curso")
        self.estado_field = MDTextField(text=aula.get("estado", "Libre"), hint_text="Estado", readonly=True, on_focus=self._toggle_estado_menu)
        self.especialidad_field = MDTextField(text=aula.get("especialidad", "Computación"), hint_text="Especialidad")

        # Menú desplegable para estado
        menu_items = [
            {"text": estado, "on_release": lambda x=estado: self._set_estado(x, self.estado_field)}
            for estado in OPCIONES_ESTADO
        ]
        self.menu_estado = MDDropdownMenu(caller=self.estado_field, items=menu_items, width_mult=3)

        # Diálogo
        content_cls = MDBoxLayout(
            self.nombre_field,
            self.curso_field,
            self.estado_field,
            self.especialidad_field,
            orientation="vertical",
            spacing="10dp",
            size_hint_y=None,
            height="260dp",
        )
        
        self.dialog_editar = MDDialog(
            title=f"Editar {aula.get('nombre', 'Aula')}",
            type="custom",
            content_cls=content_cls,
            buttons=[
                MDRaisedButton(text="Cancelar", on_release=lambda x: self.dialog_editar.dismiss()),
                MDRaisedButton(
                    text="Guardar",
                    on_release=lambda x: self._guardar_aula(
                        aula, self.nombre_field.text, self.curso_field.text, 
                        self.estado_field.text, self.especialidad_field.text
                    )
                ),
            ],
        )
        self.dialog_editar.open()
    
    def _toggle_estado_menu(self, instance, value):
        if value:
            self.menu_estado.open()
        else:
            self.menu_estado.dismiss()


    def _set_estado(self, estado, field):
        field.text = estado
        self.menu_estado.dismiss()

    def _guardar_aula(self, aula, nuevo_nombre, nuevo_curso, nuevo_estado, nueva_especialidad):
        # Renombrado a _guardar_aula
        aula["nombre"] = nuevo_nombre
        aula["curso"] = nuevo_curso
        aula["estado"] = nuevo_estado
        aula["especialidad"] = nueva_especialidad

        try:
            data = {
                "nombre": nuevo_nombre,
                "curso": nuevo_curso,
                "estado": nuevo_estado,
                "especialidad": nueva_especialidad
            }
            # Se usa PUT para actualizar
            requests.put(f"{API_URL}/aula/{aula['id']}", json=data)
        except Exception:
            pass 

        self.dialog_editar.dismiss()
        self.cargar_aulas() 
        
    def open_camera(self, *args):
        self.manager.current = "scanner"


# =====================================
# CLASE DE VISTA DEL ESCÁNER
# =====================================
class ScannerScreen(Screen):
    # Uso de IDs del .kv y renombrado de métodos internos
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.zbarcam = ZBarCam()
        self.zbarcam.size_hint_y = 0.8 # Ocupa más espacio de la pantalla
        
        # Contenedor para la cámara, se puede definir en el .kv pero para este caso simple se mantiene aquí
        layout = MDBoxLayout(orientation="vertical")
        layout.add_widget(self.zbarcam)
        
        # Label y botón definidos en el .kv o pueden seguir aquí
        self.ids_dict = self.ids if hasattr(self, 'ids') else {}

        self.label_info = MDLabel(text="Escaneando...", halign="center", size_hint_y=0.1, font_style="Subtitle1")
        layout.add_widget(self.label_info)

        btn_volver = MDRaisedButton(text="Volver", pos_hint={"center_x": 0.5}, on_release=self._volver)
        layout.add_widget(btn_volver)
        self.add_widget(layout)
        
        self.event = None

    def on_enter(self):
        # Inicia la cámara y la comprobación cuando la pantalla es visible
        self.zbarcam.start()
        self.event = Clock.schedule_interval(self._check_qr, 0.5)

    def on_leave(self):
        # Detiene la cámara y el evento cuando la pantalla es oculta
        self.zbarcam.stop()
        if self.event:
            Clock.unschedule(self.event)
            self.event = None

    def _check_qr(self, dt):
        if self.zbarcam.symbols:
            qr_data = self.zbarcam.symbols[0].data.decode("utf-8")
            self.label_info.text = f"Código detectado: {qr_data}"
            
            # Detiene la comprobación inmediatamente para evitar múltiples lecturas
            Clock.unschedule(self.event)
            self.zbarcam.stop() 
            self._handle_qr(qr_data)

    def _handle_qr(self, data):
        # Renombrado a _handle_qr
        if data.startswith("http://") and ("/aula/" in data or "/curso/" in data):
            try:
                response = requests.get(data)
                if response.status_code == 200:
                    info = response.json()
                    texto = "\n".join([f"{k}: {v}" for k, v in info.items()])
                    dialog = MDDialog(
                        title="Datos obtenidos",
                        text=texto,
                        buttons=[MDRaisedButton(text="Cerrar", on_release=lambda x: dialog.dismiss())]
                    )
                    dialog.open()
                else:
                    MDDialog(title="Error", text=f"No se pudo obtener información.\nCódigo: {response.status_code}").open()
            except Exception as e:
                MDDialog(title="Error de conexión", text=str(e)).open()
        else:
            dialog = MDDialog(title="Código no reconocido", text=f"Contenido: {data}")
            dialog.open()

    def _volver(self, *args):
        # Renombrado a _volver
        self.manager.current = "main"


# =====================================
# APP PRINCIPAL (Carga el .kv y define el tema)
# =====================================
class qr_app(MDApp):
    def build(self):
        # Configuración del tema (Mejora estética)
        self.theme_cls.theme_style = "Dark" # O "Light"
        self.theme_cls.primary_palette = "Indigo" # Un color más vibrante
        self.theme_cls.accent_palette = "Teal" 

        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(ScannerScreen(name="scanner"))
        return sm
    
    # Kivy buscará automáticamente el archivo qr_app.kv
    # Si lo renombras, debes cambiar 'QRApp' al nuevo nombre (ej: 'MiApp.kv')

if __name__ == "__main__":
    qr_app().run()