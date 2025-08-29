from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
from models import actualizar_usuario, obtener_usuario_por_cedula
from ui_utils import centrar_ventana,aplicar_icono
import re
from PyQt5.QtCore import QDate,Qt, QSize


class EditarUsuario(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editar Usuario")
        self.resize(300, 200)
        centrar_ventana(self)
        layout = QVBoxLayout()
        aplicar_icono(self)

        

        layout.addWidget(QLabel("Cedula:"))
        self.input_cedula = QLineEdit()
        layout.addWidget(self.input_cedula)

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

        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_usuario)
        layout.addWidget(self.btn_editar)

        self.setLayout(layout)
        self.input_cedula.returnPressed.connect(self.buscar_por_cedula)
        
    def validar_correo(self, email: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    def buscar_por_cedula(self):
        cedula = self.input_cedula.text().strip()
        # if not self.validar_correo(cedula):
        #     QMessageBox.warning(self, "Error", "Ingrese un correo electrónico válido.")
        #     return

        user = obtener_usuario_por_cedula(cedula)
        if not user:
            QMessageBox.information(self, "Sin resultados", "No existe un usuario con ese correo.")
            self.usuario_cedula = None
            self.input_cedula.clear()
            self.input_name.clear()
            self.input_password.clear()
            self.combo_role.setCurrentIndex(0)
            return

        # user = (id, cedula, nombre, email, rol)
        self.usuario_cedula = user[1]
        self.input_cedula.setText(str(user[1]))
        self.input_email.setText(user[3])
        self.input_name.setText(user[2])

        # Seleccionar rol en el combo
        rol = user[4] or "user"
        idx = self.combo_role.findText(rol, Qt.MatchFixedString)
        self.combo_role.setCurrentIndex(idx if idx >= 0 else 0)

        # no traemos contraseña (hash), el cambio es opcional:
        self.input_password.clear()

        

    def editar_usuario(self):
        if not self.usuario_cedula:
            QMessageBox.warning(self, "Atención", "Busque primero un usuario por correo y cárguelo.")
            return

        nombre = self.input_name.text().strip()
        email  = self.input_email.text().strip().lower()
        passwd = self.input_password.text().strip()
        rol    = self.combo_role.currentText()

        if not nombre or not self.validar_correo(email):
            QMessageBox.warning(self, "Error", "Nombre y correo válido son obligatorios.")
            return

        # Si passwd == "" => no cambia password
        ok = actualizar_usuario(self.usuario_cedula, nombre, email, passwd if passwd else None, rol)
        if ok:
            QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente.")
            self.usuario_cedula = None
            self.input_cedula.clear()
            self.input_name.clear()
            self.input_email.clear()
            self.input_password.clear()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "No se pudo actualizar (correo duplicado u otro problema).")
