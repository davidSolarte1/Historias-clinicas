from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QDateEdit
)
from PyQt5.QtCore import QDate
from models import guardar_historia

class UserPanel(QWidget):
    def __init__(self, user_id, nombre):
        super().__init__()
        self.user_id = user_id
        self.nombre = nombre

        self.setWindowTitle(f"Panel Usuario - {self.nombre}")
        self.setGeometry(200, 200, 500, 400)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Bienvenido {self.nombre}"))

        # Formulario
        form_layout = QFormLayout()

        self.input_num_carpeta = QLineEdit()
        form_layout.addRow("Número de Carpeta:", self.input_num_carpeta)

        self.input_cedula = QLineEdit()
        form_layout.addRow("Cédula del Paciente:", self.input_cedula)

        self.combo_servicio = QComboBox()
        self.combo_servicio.addItems([
            "Urgencias",
            "Cirugía",
            "Oncoematologia",
            "Neonatos",
            "Ginecología",
            "Sala de Partos",
            "UCI Adultos",
            "URPA",
            "Especialidades Quirurgicas Ortopedia",
            "Medicina Interna",
            "Especialidaddes 4 piso Contributivo",
            "Especialidades 5 piso Pension",

        ])
        form_layout.addRow("Servicio:", self.combo_servicio)

        self.input_fecha = QDateEdit()
        self.input_fecha.setDate(QDate.currentDate())
        self.input_fecha.setCalendarPopup(True)
        form_layout.addRow("Fecha de Recepción:", self.input_fecha)

        layout.addLayout(form_layout)

        # Botón guardar
        self.btn_guardar = QPushButton("Guardar Historia")
        self.btn_guardar.clicked.connect(self.guardar_historia)
        layout.addWidget(self.btn_guardar)

        self.setLayout(layout)

    def guardar_historia(self):
        num_carpeta = self.input_num_carpeta.text().strip()
        cedula = self.input_cedula.text().strip()
        servicio = self.combo_servicio.currentText()
        fecha = self.input_fecha.date().toString("yyyy-MM-dd")

        if not num_carpeta or not cedula:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos.")
            return

        guardar_historia(num_carpeta, cedula, servicio, fecha, self.user_id)
        QMessageBox.information(self, "Éxito", "Historia registrada correctamente.")

        # Limpiar campos
        self.input_num_carpeta.clear()
        self.input_cedula.clear()
        self.combo_servicio.setCurrentIndex(0)
        self.input_fecha.setDate(QDate.currentDate())
