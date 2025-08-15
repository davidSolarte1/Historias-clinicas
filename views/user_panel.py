from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QDateEdit, QTableWidget,
    QTableWidgetItem
)
from PyQt5.QtCore import QDate
from functools import partial
from models import guardar_historia, obtener_historias_devueltas, obtener_historia_por_id, actualizar_historia_revisada
from ui_utils import centrar_ventana


class UserPanel(QWidget):
    def __init__(self, user_id, nombre):
        super().__init__()
        self.user_id = user_id
        self.nombre = nombre


        # control de edición
        self.modo_edicion = False
        self.historia_edit_id = None


        self.setWindowTitle(f"Panel Usuario - {self.nombre}")
        self.resize(500, 400)
        centrar_ventana(self)

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

        # ---------- Tabla de devueltas  ----------
        self.lbl_devueltas = QLabel("Historias devueltas (pendientes de corregir):")
        self.tbl_devueltas = QTableWidget()
        self.tbl_devueltas.setColumnCount(7)
        self.tbl_devueltas.setHorizontalHeaderLabels([
            "ID", "Carpeta", "Cédula", "Servicio", "Fecha", "Observación", "Revisar"
        ])
        self.setLayout(layout)
        self.cargar_devueltas()  

    def guardar_historia(self):
        num_carpeta = self.input_num_carpeta.text().strip()
        cedula = self.input_cedula.text().strip()
        servicio = self.combo_servicio.currentText()
        fecha = self.input_fecha.date().toString("yyyy-MM-dd")

        if not num_carpeta or not cedula:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos.")
            return
        
        try:
            if self.modo_edicion and self.historia_edit_id:
                # Guardar revisión (misma historia, estado 'revisada')
                actualizar_historia_revisada(self.historia_edit_id, num_carpeta, cedula, servicio, fecha)
                QMessageBox.information(self, "Éxito", "Historia revisada y actualizada correctamente.")
                self._salir_modo_edicion()
                self.cargar_devueltas()
            else:
                # Registro normal (estado 'registrada' en guardar_historia)
                guardar_historia(num_carpeta, cedula, servicio, fecha, self.user_id)
                QMessageBox.information(self, "Éxito", "Historia registrada correctamente.")
                self._limpiar_form()
                # por si una estaba devuelta y la resolviste “manualmente”:
                self.cargar_devueltas()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def cargar_devueltas(self):
        devueltas = obtener_historias_devueltas(self.user_id)

        # Si no hay, asegúrate de que no queden en pantalla
        parent_layout = self.layout()
        if not devueltas:
            # si ya estaban agregadas, quítalas del layout
            if parent_layout.indexOf(self.lbl_devueltas) != -1:
                parent_layout.removeWidget(self.lbl_devueltas)
                self.lbl_devueltas.setParent(None)
            if parent_layout.indexOf(self.tbl_devueltas) != -1:
                parent_layout.removeWidget(self.tbl_devueltas)
                self.tbl_devueltas.setParent(None)
            return

        # Si hay, agrégalas al layout si aún no están
        if self.layout().indexOf(self.lbl_devueltas) == -1:
            parent_layout.addWidget(self.lbl_devueltas)
        if self.layout().indexOf(self.tbl_devueltas) == -1:
            parent_layout.addWidget(self.tbl_devueltas)

        # poblar tabla
        self.tbl_devueltas.setRowCount(0)
        for row in devueltas:
            # row: (id, numero_carpeta, cedula_paciente, servicio, fecha_recepcion, observacion)
            row_idx = self.tbl_devueltas.rowCount()
            self.tbl_devueltas.insertRow(row_idx)
            for col_idx in range(6):
                self.tbl_devueltas.setItem(row_idx, col_idx, QTableWidgetItem(str(row[col_idx])))

            historia_id = row[0]
            btn_revisar = QPushButton("Revisar")
            btn_revisar.clicked.connect(partial(self._cargar_en_form, historia_id))
            self.tbl_devueltas.setCellWidget(row_idx, 6, btn_revisar)

    # ---------- Acciones de edición ----------
    def _cargar_en_form(self, historia_id: int):
        row = obtener_historia_por_id(historia_id)
        if not row:
            QMessageBox.critical(self, "Error", "No se encontró la historia.")
            return

        # row: (id, numero_carpeta, cedula_paciente, servicio, fecha_recepcion, observacion, estado)
        _, num, ced, srv, fecha, *_ = row

        self.input_num_carpeta.setText(str(num))
        self.input_cedula.setText(str(ced))

        idx = self.combo_servicio.findText(str(srv))
        self.combo_servicio.setCurrentIndex(idx if idx >= 0 else 0)

        try:
            y, m, d = map(int, str(fecha).split("-"))
            self.input_fecha.setDate(QDate(y, m, d))
        except Exception:
            self.input_fecha.setDate(QDate.currentDate())

        # activar modo edición
        self.modo_edicion = True
        self.historia_edit_id = historia_id
        self.btn_guardar.setText("Guardar revisión")

        QMessageBox.information(self, "Edición", "Puedes corregir la historia y guardar la revisión.")

    def _salir_modo_edicion(self):
        self.modo_edicion = False
        self.historia_edit_id = None
        self.btn_guardar.setText("Guardar Historia")
        self._limpiar_form()

    def _limpiar_form(self):
        self.input_num_carpeta.clear()
        self.input_cedula.clear()
        self.combo_servicio.setCurrentIndex(0)
        self.input_fecha.setDate(QDate.currentDate())


