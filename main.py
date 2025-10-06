from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField


try:
    from jnius import autoclass, cast
except ImportError:
    class MockActivity:
        mActivity = None


    def autoclass(name):
        print(f"[Mock jnius] autoclass llamado con {name}")
        if name == "org.kivy.android.PythonActivity":
            return MockActivity
        return lambda *args, **kwargs: None


    def cast(*args, **kwargs):
        print("[Mock jnius] cast llamado")
        return None




# Clases de Android necesarias para usar el escáner de QR
PythonActivity = autoclass('org.kivy.android.PythonActivity')
IntentIntegrator = autoclass('com.google.zxing.integration.android.IntentIntegrator')
IntentResult = autoclass('com.google.zxing.integration.android.IntentResult')




class QRScanner(MDBoxLayout):
    def __init__(self, **kwargs):
        # Layout principal vertical
        super().__init__(orientation='vertical', **kwargs)


        # Barra superior con botón de login
        self.toolbar = MDTopAppBar(
            title="Lector QR",
            left_action_items=[["account", lambda x: self.show_login_dialog()]]
        )
        self.add_widget(self.toolbar)


        # Texto inicial
        self.label = MDLabel(text="Pulsa para escanear QR", halign="center")
        self.add_widget(self.label)


        # Botón que inicia el escaneo
        self.button = MDRaisedButton(
            text="Escanear",
            pos_hint={"center_x": 0.5},
            on_release=self.start_scan
        )
        self.add_widget(self.button)


        # Referencia a la actividad de Android
        self.activity = PythonActivity.mActivity


        # Variables para login
        self.dialog = None
        self.username = None
        self.password = None
        self.admin_logged = False


    def start_scan(self, *args):
        if self.activity is None:  
            # Modo PC / pruebas
            self.label.text = "📷 Simulación: aquí se abriría el escáner QR"
            return


        # --- Solo en Android ---
        integrator = IntentIntegrator(self.activity)
        if integrator:
            integrator.setDesiredBarcodeFormats(IntentIntegrator.QR_CODE)  # Solo QR
            integrator.setPrompt("Escanea un código QR")
            integrator.setCameraId(0)  # Cámara trasera
            integrator.setBeepEnabled(True)
            integrator.initiateScan()
        else:
            self.label.text = "No se pudo iniciar el escáner QR"




    def on_activity_result(self, requestCode, resultCode, data):
        # Recibe el resultado del escaneo
        result = IntentResult.parseActivityResult(requestCode, resultCode, data)
        if result:
            contents = result.getContents()
            if contents:
                self.label.text = f"QR detectado:\n{contents}"
            else:
                self.label.text = "Escaneo cancelado"


    # ================== LOGIN ==================
    def show_login_dialog(self):
        if not self.dialog:
            self.username = MDTextField(
                hint_text="Usuario",
                required=True
            )
            self.password = MDTextField(
                hint_text="Contraseña",
                password=True,
                required=True
            )


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
        if self.username.text == "admin" and self.password.text == "1234":
            self.admin_logged = True
            self.dialog.dismiss()
            self.label.text = "Sesión de administrador iniciada"
        else:
            self.username.error = True
            self.password.error = True




class QRApp(MDApp):
    def build(self):
        return QRScanner()




if __name__ == '__main__':
    QRApp().run()



