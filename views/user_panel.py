from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QToolButton,
    QComboBox, QPushButton, QMessageBox, QDateEdit, QTableWidget,
    QTableWidgetItem,QHeaderView,QGroupBox, QHBoxLayout
)
from PyQt5.QtGui import QIntValidator,QRegularExpressionValidator,QIcon, QColor
from PyQt5.QtCore import QDate,QRegularExpression,Qt, QSize
from functools import partial
from models import guardar_historia, obtener_historias_devueltas, obtener_historia_por_id, actualizar_historia_revisada
from ui_utils import centrar_ventana,ruta_recurso,aplicar_icono
from datetime import date


class UserPanel(QWidget):
    def __init__(self, user_id, nombre):
        super().__init__()
        self.user_id = user_id
        self.nombre = nombre
        aplicar_icono(self)

        # control de edición
        self.modo_edicion = False
        self.historia_edit_id = None


        self.setWindowTitle(f"SIREH - {self.nombre}")
        self.resize(1100, 650)
        centrar_ventana(self)

        layout = QVBoxLayout()

        # Formulario
        form_layout = QFormLayout()

        self.input_num_carpeta = QLineEdit()
        self.input_num_carpeta.setMaxLength(6)
        self.input_num_carpeta.setValidator(QIntValidator(0, 999999))
        form_layout.addRow("Número de Carpeta:", self.input_num_carpeta)

        self.input_cedula = QLineEdit()
        regex = QRegularExpression("^[0-9]{0,15}$")  # entre 0 y 15 dígitos
        validator = QRegularExpressionValidator(regex)
        self.input_cedula.setValidator(validator)
        form_layout.addRow("Cédula del Paciente:", self.input_cedula)
        
        self.input_nombre = QLineEdit()
        form_layout.addRow("Nombre Paciente:", self.input_nombre)

        self.input_apellido = QLineEdit()
        form_layout.addRow("Apellido Paciente:", self.input_apellido)

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
            "Consultorio Ginecología",
            "Consultorio Urgencias",

        ])
        form_layout.addRow("Servicio:", self.combo_servicio)

      

        boton_layout = QVBoxLayout()
        grupo_form = QGroupBox("Registro de Historia Clínica")
        grupo_form.setLayout(form_layout)


        #Boton cerrar sesion

        self.btn_cerrar = QToolButton()
        self.btn_cerrar.setText("Salir")
        self.btn_cerrar.setIcon(QIcon(ruta_recurso("icons/cerrar-sesion.png")))
        self.btn_cerrar.setIconSize(QSize(32, 32)) 
        self.btn_cerrar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_cerrar.setFixedSize(52, 52)
        self.btn_cerrar.clicked.connect(self.cerrar_sesion)

        botbar = QHBoxLayout()
        botbar.addStretch()
        botbar.addWidget(self.btn_cerrar)

        #boton actualizar

        self.btn_actualizar = QToolButton()
        self.btn_actualizar.setText("Actualizar")
        self.btn_actualizar.setIcon(QIcon(ruta_recurso("icons/actualizar.png")))
        self.btn_actualizar.setIconSize(QSize(48, 48)) 
        self.btn_actualizar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_actualizar.setFixedSize(90, 70)
        self.btn_actualizar.clicked.connect(self.cargar_devueltas)
        
        # Botón guardar
        self.btn_guardar = QToolButton()
        self.btn_guardar.setText("Guardar Historia")
        self.btn_guardar.setIcon(QIcon(ruta_recurso("icons/boton_guardar.png")))
        self.btn_guardar.setIconSize(QSize(48, 48)) 
        self.btn_guardar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_guardar.setFixedSize(90, 70)
        self.btn_guardar.clicked.connect(self.guardar_historia)

        boton_layout.addWidget(self.btn_actualizar)
        boton_layout.addWidget(self.btn_guardar)
        hbox = QHBoxLayout()
        hbox.addWidget(grupo_form, 3)   # el formulario ocupa más espacio
        hbox.addLayout(boton_layout, 1)  # el botón al costado

        layout.addLayout(hbox)

        # ---------- Tabla de devueltas  ----------
        self.lbl_devueltas = QLabel("Historias devueltas (pendientes de corregir):")
        self.tbl_devueltas = QTableWidget()
        self.tbl_devueltas.setColumnCount(9)
        self.tbl_devueltas.setHorizontalHeaderLabels([
            "ID", "Carpeta", "Cédula", "Nombre", "Apellido" , "Servicio", "Fecha", "Observación", "Revisar"
        ])
        # que las columnas usen el ancho disponible
        header = self.tbl_devueltas.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # (opcional) filas alternadas para mejor lectura
        self.tbl_devueltas.setAlternatingRowColors(True)

        self.setLayout(layout)

        self.cargar_devueltas()  
        layout.addLayout(botbar)

    def guardar_historia(self):
        num_carpeta = self.input_num_carpeta.text().strip()
        cedula = self.input_cedula.text().strip()
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()
        servicio = self.combo_servicio.currentText()



        if not num_carpeta or not cedula:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos.")
            return
        # Validar número de carpeta (debe ser exactamente 6 dígitos)
        if not (num_carpeta.isdigit() and len(num_carpeta) == 6):
            QMessageBox.warning(self, "Error", "El número de carpeta debe contener exactamente 6 números (por ejemplo: 000123).")
            return

        # Validar cédula (solo números)
        if not cedula.isdigit():
            QMessageBox.warning(self, "Error", "La cédula/identificación solo puede contener números.")
            return

        try:
            if self.modo_edicion and self.historia_edit_id:
                # Guardar revisión (misma historia, estado 'revisada')
                actualizar_historia_revisada(self.historia_edit_id, num_carpeta, cedula, nombre, apellido, servicio)
                QMessageBox.information(self, "Éxito", "Historia revisada y actualizada correctamente.")
                self._salir_modo_edicion()
                self.cargar_devueltas()
            else:
                # Registro normal (estado 'registrada' en guardar_historia)
                guardar_historia(num_carpeta, cedula, nombre, apellido, servicio, self.user_id)
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
        # si ya estaban agregadas, quítalas del layout
        if parent_layout.indexOf(self.lbl_devueltas) == -1:
            parent_layout.addWidget(self.lbl_devueltas)
        if parent_layout.indexOf(self.tbl_devueltas) == -1:
            parent_layout.addWidget(self.tbl_devueltas)
        # poblar tabla
        self.tbl_devueltas.setRowCount(0)

        if not devueltas:
            self.tbl_devueltas.setRowCount(1)
            item = QTableWidgetItem("No existen historias devueltas.")
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QColor("gray"))
            self.tbl_devueltas.setItem(0, 0, item)
            
            # opcional: dejar el resto de columnas visualmente vacías
            for i in range(1, 8):
                empty = QTableWidgetItem("")
                empty.setFlags(Qt.NoItemFlags)  # no seleccionable
                self.tbl_devueltas.setItem(0, i, empty)
                self.tbl_devueltas.setSpan(0,0,1,9)
                self.tbl_devueltas.verticalHeader().setVisible(False)
            return
        self.tbl_devueltas.verticalHeader().setVisible(True)
        for row in devueltas:
            # row: (id, numero_carpeta, cedula_paciente, servicio, fecha_recepcion, observacion)
            row_idx = self.tbl_devueltas.rowCount()
            self.tbl_devueltas.insertRow(row_idx)
            for col_idx in range(8):
                self.tbl_devueltas.setItem(row_idx, col_idx, QTableWidgetItem(str(row[col_idx])))
            historia_id = row[0]
            btn_revisar = QPushButton("Revisar")
            btn_revisar.clicked.connect(partial(self._cargar_en_form, historia_id))
            self.tbl_devueltas.setCellWidget(row_idx, 8, btn_revisar)

    # ---------- Acciones de edición ----------
    def _cargar_en_form(self, historia_id: int):
        row = obtener_historia_por_id(historia_id)
        if not row:
            QMessageBox.critical(self, "Error", "No se encontró la historia.")
            return

        # row: (id, numero_carpeta, cedula_paciente, servicio, fecha_recepcion, observacion, estado)
        _, num, ced, nom, ape, srv, fecha, *_ = row

        self.input_num_carpeta.setText(str(num))
        self.input_cedula.setText(str(ced))
        self.input_nombre.setText(str(nom))
        self.input_apellido.setText(str(ape))

        idx = self.combo_servicio.findText(str(srv))
        self.combo_servicio.setCurrentIndex(idx if idx >= 0 else 0)



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
        self.input_nombre.clear()
        self.input_apellido.clear()
        self.combo_servicio.setCurrentIndex(0)
    
    def cerrar_sesion(self):
        from views.login import LoginWindow
        self.close()
        self.login = LoginWindow()
        self.login.show()


