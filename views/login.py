from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from models import verificar_usuario
from views.admin_panel import AdminPanel
from views.user_panel import UserPanel
from ui_utils import centrar_ventana,aplicar_icono

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIREH - Login")
        aplicar_icono(self)
        self.resize(350, 200)
        centrar_ventana(self)

        layout = QVBoxLayout()

        self.label_title = QLabel("Iniciar Sesión")
        self.label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_title)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Correo electrónico")
        layout.addWidget(self.input_email)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contraseña")
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)
        self.input_email.returnPressed.connect(self.input_password.setFocus)
        self.input_password.returnPressed.connect(self.login)

        self.btn_login = QPushButton("Iniciar Sesión")
        self.btn_login.clicked.connect(self.login)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def login(self):
        email = self.input_email.text().strip().lower()
        password = self.input_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Por favor, complete todos los campos.")
            return

        user = verificar_usuario(email, password)

        if user:
            user_id, nombre, rol = user

            self.hide()  # Ocultar login

            if rol == "admin":
                self.panel = AdminPanel(user_id, nombre)
            else:
                self.panel = UserPanel(user_id, nombre)
            self.panel.show()

        else:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas.")
