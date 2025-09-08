from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
from models import registrar_usuario, usuario_existe
from ui_utils import centrar_ventana,aplicar_icono
import re

class RegistroUsuario(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registrar Nuevo Usuario")
        self.resize(300, 200)
        centrar_ventana(self)
        layout = QVBoxLayout()
        aplicar_icono(self)

        
        layout.addWidget(QLabel("Cédula:"))
        self.input_cedula = QLineEdit()
        layout.addWidget(self.input_cedula)

        layout.addWidget(QLabel("Nombre:"))
        self.input_name = QLineEdit()
        layout.addWidget(self.input_name)


        layout.addWidget(QLabel("Correo:"))
        self.input_email = QLineEdit()
        layout.addWidget(self.input_email)

        layout.addWidget(QLabel("Rol:"))
        self.combo_role = QComboBox()
        self.combo_role.addItems(["user", "admin"])
        layout.addWidget(self.combo_role)

        self.btn_registrar = QPushButton("Registrar")
        self.btn_registrar.clicked.connect(self.registrar_usuario)
        layout.addWidget(self.btn_registrar)

        self.setLayout(layout)

    def registrar_usuario(self):
        cedula = self.input_cedula.text().strip()
        name = self.input_name.text().strip()
        email = self.input_email.text().strip().lower()
        password = self.input_cedula.text().strip()
        role = self.combo_role.currentText()

        if not email or not password or not name or not cedula:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            QMessageBox.warning(self, "Error", "Ingrese un correo electrónico válido.")
            return
        if usuario_existe(cedula):
            QMessageBox.warning(self, "Error", "El usuario ya se encuentra registrado.")
            return
        if registrar_usuario(cedula, name, email, password, role):
            QMessageBox.information(self, "Éxito", "Usuario creado correctamente.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "No se pudo crear el usuario. Intente nuevamente.")