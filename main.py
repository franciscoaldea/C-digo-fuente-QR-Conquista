# =========================
# IMPORTACIONES
# =========================

import requests                               # Cliente HTTP para comunicarse con la API REST
from kivymd.app import MDApp                  # Clase base para apps KivyMD
from kivymd.uix.boxlayout import MDBoxLayout  # Layout en caja (vertical/horizontal) de KivyMD
from kivymd.uix.label import MDLabel          # Widget para texto (labels) en KivyMD
from kivymd.uix.button import MDRaisedButton  # Botón elevado de KivyMD
from kivymd.uix.dialog import MDDialog        # Diálogo modal de KivyMD
from kivymd.uix.textfield import MDTextField  # Campo de texto de KivyMD
from kivy.uix.screenmanager import ScreenManager, Screen  # Manejo de pantallas
from kivy.clock import Clock                  # Programación de eventos temporizados
from kivy_garden.zbarcam import ZBarCam       # Cámara/lector QR (zbar)
from kivymd.uix.menu import MDDropdownMenu    # Menú desplegable de KivyMD
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget  # Items de lista con iconos
from kivymd.uix.card import MDCard            # Tarjeta visual para mostrar contenido
import logging # módulo estándar para salida de errores

# =========================
# CONSTANTES DE CONFIGURACIÓN
# =========================

# TODO: Esta url si va hardcodeada tiene que ser una ubicación
# en la web, y para eso habría que hacer un deploy en un servicio
# de hosting que corra la app Flask.
# Como alternativa, se puede implementar una URL editable por una
# ventana de la app Kivy (ver tutoriales en blog:
# https://kivy-tutoriales.blogspot.com/2025/07/interfaz-movil-para-api-web.html
# la URL por defecto de la línea que sigue es para pruebas con un servidor en una LAN
# y por lo tanto correrla sin un servidor en esa dirección va a generar un error
API_URL = "http://192.168.1.19:5000"            # URL base de la API a la que se hacen las peticiones
OPCIONES_ESTADO = ["Libre", "Ocupada", "Cerrada"]  # Estados permitidos para las aulas

# =========================
# CLASE PRINCIPAL: PANTALLA DE AULAS
# =========================
class MainScreen(Screen):
    """
    Pantalla principal de la aplicación.
    - Muestra listado de aulas.
    - Permite login de administrador.
    - Permite editar aulas si el admin está logueado.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)              # Inicializa la clase base Screen
        # Variables de estado de la pantalla
        self.dialog_login = None               # Guardará el diálogo de login (si se crea)
        self.dialog_editar = None              # Guardará el diálogo de edición de aula
        self.menu_estado = None                # Referencia al menú desplegable de estados
        self.admin_logged = False              # Booleano que indica si un admin inició sesión
        self.aulas = []                        # Lista local de aulas cargadas desde la API

    # -------------------------
    # LOGIN DE ADMINISTRADOR
    # -------------------------
    def show_login_dialog(self):
        """Muestra el cuadro de diálogo para iniciar sesión como administrador."""
        if not self.dialog_login:              # Si el diálogo aún no fue creado, lo construyo
            # Campos de texto para usuario y contraseña
            self.username_field = MDTextField(hint_text="Usuario", required=True)  # Campo usuario
            # Campo contraseña (oculto)            
            self.password_field = MDTextField(hint_text="Contraseña", password=True, required=True)

            # Contenedor vertical que agrupa los campos dentro del diálogo
            content_box = MDBoxLayout(
                self.username_field,           # primer widget dentro del box
                self.password_field,           # segundo widget dentro del box
                orientation="vertical",        # disposición vertical
                spacing="10dp",                # espacio entre widgets
                size_hint_y=None,              # altura fija (no proporcional)
                height="120dp"                 # altura específica en dp
            )
           
            # Creación del diálogo con título, contenido y botones
            self.dialog_login = MDDialog(
                title="Iniciar sesión (Admin)",# Título del diálogo
                type="custom",                 # Tipo custom para usar content_cls
                content_cls=content_box,       # Contenido personalizado (los campos)
                # Botón cancelar cierra diálogo
                # Botón entrar llama verificación
                buttons=[MDRaisedButton(text="Cancelar",
                on_release=lambda x: self.dialog_login.dismiss()),
                    MDRaisedButton(text="Entrar",
                    on_release=lambda x: self._check_login())])
        self.dialog_login.open() # Abre (muestra) el diálogo

    def _check_login(self):
        """Verifica las credenciales del administrador."""
        data = {
            "nombre_usuario": self.username_field.text,   # Toma el texto del campo usuario
            "contraseña": self.password_field.text       # Toma el texto del campo contraseña
        }

        try:
            # Petición POST a la ruta /login de la API con las credenciales
            response = requests.post(f"{API_URL}/login", json=data)
            main_label = self.ids.main_label             # Referencia al label principal (desde kv)
            aulas_container = self.ids.aulas_container   # Referencia al contenedor de aulas (desde kv)
           
            if response.status_code == 200:              # Si la API responde 200 -> login exitoso
                user = response.json()                   # Obtener datos del usuario desde la respuesta JSON
                self.admin_logged = True                 # Marcar que el admin está logueado
                self.dialog_login.dismiss()              # Cerrar el diálogo de login
                main_label.text = f"Bienvenido, {user['usuario']['nombre_usuario']}"  # Mostrar mensaje de bienvenida
                aulas_container.opacity = 1              # Hacer visible el contenedor de aulas
                aulas_container.disabled = False        # Habilitar interacción con el contenedor
                self.cargar_aulas()                     # Recargar las aulas desde la API
            else:
                # Credenciales incorrectas: mostrar mensaje en el label principal
                main_label.text = "Usuario o contraseña incorrectos"
        except Exception as e:
            # En caso de error de conexión u otra excepción, mostrar mensaje de error
            self.ids.main_label.text = f"Error de conexión: {e}"

    # -------------------------
    # CARGA DE AULAS
    # -------------------------
    def cargar_aulas(self):
        """Obtiene y muestra todas las aulas desde la API."""
        aulas_container = self.ids.aulas_container   # Referencia al contenedor donde se agregan tarjetas
        aulas_container.clear_widgets()              # Limpiar widgets previos para refrescar la lista

        try:
            # Petición GET a la ruta /aulas para obtener todas las aulas
            response = requests.get(f"{API_URL}/aulas")
            if response.status_code == 200:
                self.aulas = response.json()         # Guardar el JSON devuelto en self.aulas
            else:
                self.aulas = []                      # Si error HTTP, dejar lista vacía
                self.ids.main_label.text = f"Error al obtener aulas: {response.status_code}"  # Mostrar código de error
        except Exception:
            # Si falla la conexión, proporcionar datos de ejemplo (fallback)
            self.aulas = [
                {"id": 1, "nombre": "Aula 1", "curso": "3°A", "estado": "Libre", "especialidad": "Computación"},
                {"id": 2, "nombre": "Aula 2", "curso": "4°B", "estado": "Ocupada", "especialidad": "Computación"},
                {"id": 3, "nombre": "Aula 3", "curso": "5°A", "estado": "Cerrada", "especialidad": "Computación"},
                {"id": 4, "nombre": "Aula 4", "curso": "6°A", "estado": "Libre", "especialidad": "Computación"},
            ]

        # Iterar por cada aula y crear su representación visual
        for aula in self.aulas:
            self.mostrar_aula(aula)

    # -------------------------
    # REPRESENTACIÓN DE UNA AULA
    def mostrar_aula(self, aula):
        iconos = {"Libre": "check-circle", "Ocupada": "alert-circle", "Cerrada": "close-circle"}
        color_estado = {"Libre": (0, 0.6, 0, 1), "Ocupada": (0.8, 0.4, 0, 1), "Cerrada": (0.6, 0, 0, 1)}
        estado = aula.get('estado', 'Cerrada')

        card = MDCard(
            orientation="vertical",
            padding="10dp",
            spacing="10dp",
            size_hint_y=None,
            height="120dp",
            ripple_behavior=True
        )

        content_layout = MDBoxLayout(orientation='horizontal', padding="5dp", spacing="10dp")

        icon_widget = IconLeftWidget(
            icon=iconos.get(estado, "help-circle"),
            theme_text_color="Custom",
            text_color=color_estado.get(estado, (0.5, 0.5, 0.5, 1))
        )
        content_layout.add_widget(icon_widget)

        info_label = MDLabel(
            text=(
                f"[b]{aula['nombre']}[/b] ([color={self._get_hex_color(color_estado.get(estado))}]{estado}[/color])\n"
                f"Curso: {aula.get('curso', '-')}\n"
                f"Turno: {aula.get('turno', '-')}\n"
                f"Especialidad: {aula.get('especialidad', '-')}"
            ),
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
        """Convierte (r,g,b,a) a formato hexadecimal."""
        if not rgba or len(rgba) < 3:               # Si no viene color válido, devuelve gris
            return "#808080"
        # Convertir cada componente (0-1) a 0-255 y formatear como hex
        return f"#{int(rgba[0]*255):02x}{int(rgba[1]*255):02x}{int(rgba[2]*255):02x}"

    # -------------------------
    # EDICIÓN DE AULAS
    # -------------------------
    def _editar_aula(self, aula):
        """Abre un diálogo para editar los datos de un aula."""
        # Crear campos prellenados con los valores actuales del aula
        self.nombre_field = MDTextField(text=aula.get("nombre", ""), hint_text="Nombre del aula")
        self.curso_field = MDTextField(text=aula.get("curso", ""), hint_text="Curso")
        self.estado_field = MDTextField(
            text=aula.get("estado", "Libre"),        # Estado actual o Libre por defecto
            hint_text="Estado",
            readonly=True                            # Campo readonly para usar menú en lugar de edición libre
        )
        # Asignar comportamiento táctil para abrir el menú (se sobreescribe on_touch_down)
        self.estado_field.on_touch_down = lambda *args: self._open_estado_wrapper(*args)

        self.especialidad_field = MDTextField(text=aula.get("especialidad", "Computación"), hint_text="Especialidad")

        # Preparar items del menú con acciones on_release que setean el estado
        menu_items = [
            {"text": estado, "on_release": lambda x=estado: self._set_estado(x, self.estado_field)}
            for estado in OPCIONES_ESTADO
        ]
        # Crear el menú desplegable asociado al campo estado
        self.menu_estado = MDDropdownMenu(caller=self.estado_field, items=menu_items, width_mult=3)

        # Contenedor vertical que agrupa los campos dentro del diálogo de edición
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

        # Crear el diálogo de edición con botones Cancelar/Guardar
        self.dialog_editar = MDDialog(
            title=f"Editar {aula.get('nombre', 'Aula')}",  # Título dinámico según nombre del aula
            type="custom",                                 # Tipo custom para usar content_cls
            content_cls=content_cls,                       # Contenido personalizado
            buttons=[
                MDRaisedButton(text="Cancelar", on_release=lambda x: self.dialog_editar.dismiss()),  # Cerrar sin guardar
                MDRaisedButton(
                    text="Guardar",                      # Botón que guarda cambios
                    on_release=lambda x: self._guardar_aula(
                        aula, self.nombre_field.text, self.curso_field.text,
                        self.estado_field.text, self.especialidad_field.text
                    )
                ),
            ],
        )
        self.dialog_editar.open()                      # Abrir diálogo de edición
        
    def _open_estado_wrapper(self, *args):
        """Wrapper para manejar llamadas on_touch_down que pueden venir con distintos argumentos."""
        if len(args) == 2:                            # Espera (instance, touch)
            instance, touch = args
            return self._open_estado_menu(instance, touch)  # Llamar al método real con esos argumentos
        return False                                  # Si no coincide la firma, devolver False

    # Nota: _open_estado_menu se asume definida más abajo o en otro lugar; si no existe hay que implementarla.
    # (En el código original que compartiste no está la definición; puede causar un error en tiempo de ejecución.)

    def _set_estado(self, estado, field):
        """Selecciona un estado del menú (se llama desde los items del menú)."""
        field.text = estado                          # Actualiza el texto del campo con el estado seleccionado
        self.menu_estado.dismiss()                   # Cierra el menú desplegable

    def _guardar_aula(self, aula, nuevo_nombre, nuevo_curso, nuevo_estado, nueva_especialidad):
        """Guarda los cambios en un aula (envía un PUT a la API)."""
        # Actualizar el diccionario local del aula con los nuevos valores
        aula.update({
            "nombre": nuevo_nombre,
            "curso": nuevo_curso,
            "estado": nuevo_estado,
            "especialidad": nueva_especialidad
        })

        try:
            data = {
                "nombre": nuevo_nombre,
                "curso": nuevo_curso,
                "estado": nuevo_estado,
                "especialidad": nueva_especialidad
            }
            # Enviar petición PUT a la API para persistir cambios
            requests.put(f"{API_URL}/aula/{aula['id']}", json=data)
        except Exception:
            # Silenciar excepciones en este bloque (mejor loguearlas en producción)
            pass

        self.dialog_editar.dismiss()                  # Cerrar diálogo de edición
        self.cargar_aulas()                            # Volver a cargar aulas para actualizar la interfaz

    # -------------------------
    # CÁMARA / ESCÁNER
    # -------------------------
    def open_camera(self, *args):
        """Cambia a la pantalla del escáner QR."""
        self.manager.current = "scanner"               # Pide al ScreenManager que muestre la pantalla 'scanner'

# =========================
# CLASE DE ESCÁNER QR
# =========================
class ScannerScreen(Screen):
    """
    Pantalla encargada de usar la cámara para leer códigos QR.
    Al detectar un QR, consulta la API y muestra los datos del aula.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)                    # Inicializa la Screen base
        self.zbarcam = ZBarCam()                      # Instancia del componente lector de QR
        self.zbarcam.size_hint_y = 0.8                # Ajusta el tamaño vertical del widget cámara

        # Construcción del layout de la pantalla
        layout = MDBoxLayout(orientation="vertical")  # Layout vertical principal
        layout.add_widget(self.zbarcam)                # Agrega el widget de la cámara al layout

        # Label que muestra estado/resultado del escaneo
        self.label_info = MDLabel(text="Escaneando...", halign="center", size_hint_y=0.1, font_style="Subtitle1")
        layout.add_widget(self.label_info)            # Agrega el label al layout

        # Botón para volver a la pantalla principal
        btn_volver = MDRaisedButton(text="Volver", pos_hint={"center_x": 0.5}, on_release=self._volver)
        layout.add_widget(btn_volver)                 # Agrega botón al layout

        self.add_widget(layout)                       # Añade todo el layout a la pantalla
        self.event = None                             # Referencia al evento programado (Clock)

    def on_enter(self):
        """Inicia el escaneo cuando la pantalla se muestra."""
        self.zbarcam.start()                          # Inicia la cámara / lector
        self.event = Clock.schedule_interval(self._check_qr, 0.5)  # Programa comprobación de QR cada 0.5s

    def on_leave(self):
        """Detiene el escaneo cuando se abandona la pantalla."""
        self.zbarcam.stop()                           # Detiene la cámara
        if self.event:
            Clock.unschedule(self.event)              # Cancelar el evento si existe
            self.event = None

    def _check_qr(self, dt):
        """Detecta si se escaneó un código QR."""
        if self.zbarcam.symbols:                      # Si la cámara detectó símbolos (QR)
            qr_data = self.zbarcam.symbols[0].data.decode("utf-8")  # Tomar el primer símbolo y decodificar bytes a string
            self.label_info.text = f"Código detectado: {qr_data}"  # Mostrar código en el label

            # Evitar lecturas repetidas: cancelar el evento y detener la cámara
            Clock.unschedule(self.event)
            self.zbarcam.stop()
            self._handle_qr(qr_data)                 # Procesar el contenido del QR

    def _handle_qr(self, data):
        """Procesa el código QR y navega a la pantalla de información del aula."""
        # Si el contenido es una URL que apunta a /aula/, intentar obtener los datos
        if data.startswith("http://") and "/aula/" in data:
            try:
                response = requests.get(data)        # Petición GET a la URL extraída del QR
                if response.status_code == 200:
                    aula = response.json()           # Obtener datos JSON del aula

                    # Si la pantalla 'info' ya existe, actualizarla
                    if "info" in self.manager.screen_names:
                        info_screen = self.manager.get_screen("info")
                        info_screen.aula_data = aula
                        info_screen.on_pre_enter()   # Forzar actualización previa a mostrar
                    else:
                        # Crear una nueva pantalla AulaInfoScreen y agregar al manager
                        info_screen = AulaInfoScreen(name="info", aula_data=aula)
                        self.manager.add_widget(info_screen)

                    # Navegar a la pantalla de información
                    self.manager.current = "info"
                else:
                    # Mostrar diálogo de error si la API devolvió un código distinto a 200
                    MDDialog(
                        title="Error",
                        text=f"No se pudo obtener la información del aula.\nCódigo: {response.status_code}"
                    ).open()
            except Exception as e:
                # En caso de excepción de red, mostrar diálogo con el error
                MDDialog(title="Error de conexión", text=str(e)).open()
        else:
            # Si el QR no contiene la URL esperada, mostrar diálogo indicando que no se reconoció
            MDDialog(
                title="Código no reconocido",
                text=f"Contenido: {data}"
            ).open()

    def _volver(self, *args):
        """Vuelve a la pantalla principal."""
        self.manager.current = "main"                 # Cambia al nombre de pantalla 'main'

# =========================
# CLASE DE VISTA DE INFORMACIÓN DE AULA
class AulaInfoScreen(Screen):
    """Muestra la información de un aula después de escanear un código QR."""

    def __init__(self, aula_data=None, **kwargs):
        super().__init__(**kwargs)
        self.aula_data = aula_data or {}

        layout = MDBoxLayout(orientation="vertical", padding="20dp", spacing="15dp")

        self.label_titulo = MDLabel(text="Información del Aula", halign="center", font_style="H5")
        layout.add_widget(self.label_titulo)

        self.label_info = MDLabel(
            halign="left",
            valign="center",
            font_style="Body1",
            markup=True
        )
        layout.add_widget(self.label_info)

        btn_volver = MDRaisedButton(
            text="Volver",
            pos_hint={"center_x": 0.5},
            on_release=self.volver_main
        )
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def on_pre_enter(self):
        """Actualiza la información antes de mostrar la pantalla."""
        if not self.aula_data:
            self.label_info.text = "No hay datos disponibles."
            return

        self.label_info.text = (
            f"[b]Nombre:[/b] {self.aula_data.get('nombre', '-')}\n"
            f"[b]Curso:[/b] {self.aula_data.get('curso', '-')}\n"
            f"[b]Estado:[/b] {self.aula_data.get('estado', '-')}\n"
            f"[b]Especialidad:[/b] {self.aula_data.get('especialidad', '-')}\n"
            f"[b]Turno:[/b] {self.aula_data.get('turno', '-')}\n"
        )

    def volver_main(self, *args):
        self.manager.current = "main"
           # Cambia al screen 'main'

# =========================
# APP PRINCIPAL
# =========================
class qr_app(MDApp):
    """Clase principal que configura el tema y carga las pantallas."""

    def build(self):
        # Configuración visual del tema (KivyMD)
        self.theme_cls.theme_style = "Dark"           # Estilo oscuro
        self.theme_cls.primary_palette = "Indigo"     # Paleta primaria
        self.theme_cls.accent_palette = "Teal"        # Paleta de acento
       
        # Crear ScreenManager y agregar las pantallas principales
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))        # Pantalla principal
        sm.add_widget(ScannerScreen(name="scanner"))  # Pantalla del escáner
        sm.add_widget(AulaInfoScreen(name="info"))    # Pantalla de info (vacía por defecto)

        return sm                                     # Retornar el gestor de pantallas como root widget

# =========================
# EJECUCIÓN DE LA APLICACIÓN
# =========================
if __name__ == "__main__":
    # Inicializa y ejecuta la aplicación KivyMD
    # Envolvemos todo en un manejador de fallas y en caso
    # que tire algo, lo atajamos, usamos el servicio de
    # salida de depuración, y lo largamos para que la app
    # no cuelgue
    # TODO: implementar lógica de depuración más fina
    try:
        qr_app().run()
    except Exception as e:
        logging.debug("Ocurrió una excepción: %s" % str(e))
        raise e

