from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
from models import registrar_usuario

class RegistroUsuario(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registrar Nuevo Usuario")
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nombre:"))
        self.input_name = QLineEdit()
        layout.addWidget(self.input_name)


        layout.addWidget(QLabel("Correo:"))
        self.input_email = QLineEdit()
        layout.addWidget(self.input_email)

        layout.addWidget(QLabel("Contraseña:"))
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)

        layout.addWidget(QLabel("Rol:"))
        self.combo_role = QComboBox()
        self.combo_role.addItems(["user", "admin"])
        layout.addWidget(self.combo_role)

        self.btn_registrar = QPushButton("Registrar")
        self.btn_registrar.clicked.connect(self.registrar_usuario)
        layout.addWidget(self.btn_registrar)

        self.setLayout(layout)

    def registrar_usuario(self):
        name = self.input_name.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()
        role = self.combo_role.currentText()

        if not email or not password or not name:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return

        if registrar_usuario(name, email, password, role):
            QMessageBox.information(self, "Éxito", "Usuario creado correctamente.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "El usuario ya existe.")