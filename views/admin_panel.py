from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QDateEdit, QTextEdit, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QDate
from models import obtener_historias, obtener_enfermeros, agregar_observacion, exportar_reporte_excel
from views.registro_usuario import RegistroUsuario
import pandas as pd

class AdminPanel(QWidget):
    def __init__(self, user_id, nombre):
        super().__init__()
        self.user_id = user_id
        self.nombre = nombre
        self.historia_seleccionada = None

        self.setWindowTitle(f"Panel Administrador - {self.nombre}")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Bienvenido Admin: {self.nombre}"))

        # Filtros
        filtros_layout = QHBoxLayout()

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDate(QDate.currentDate().addMonths(-1))
        filtros_layout.addWidget(QLabel("Desde:"))
        filtros_layout.addWidget(self.fecha_inicio)

        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDate(QDate.currentDate())
        filtros_layout.addWidget(QLabel("Hasta:"))
        filtros_layout.addWidget(self.fecha_fin)

        self.combo_enfermero = QComboBox()
        self.combo_enfermero.addItem("Todos")
        for enfermero in obtener_enfermeros():
            self.combo_enfermero.addItem(enfermero[1], enfermero[0])  # nombre, id
        filtros_layout.addWidget(QLabel("Enfermero:"))
        filtros_layout.addWidget(self.combo_enfermero)

        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.clicked.connect(self.cargar_historias)
        filtros_layout.addWidget(self.btn_filtrar)

        layout.addLayout(filtros_layout)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Carpeta", "Cédula", "Servicio", "Fecha", "Usuario"])
        self.tabla.cellClicked.connect(self.seleccionar_historia)
        layout.addWidget(self.tabla)

        # Observaciones
        self.txt_observacion = QTextEdit()
        layout.addWidget(QLabel("Observación:"))
        layout.addWidget(self.txt_observacion)

        self.btn_guardar_obs = QPushButton("Guardar Observación")
        self.btn_guardar_obs.clicked.connect(self.guardar_observacion)
        layout.addWidget(self.btn_guardar_obs)
        
        #Exportar a EXCEL
        self.btn_exportar_excel = QPushButton("Exportar a Excel")
        self.btn_exportar_excel.clicked.connect(self.generar_reporte)
        layout.addWidget(self.btn_exportar_excel)

        #Registrar Usuarios
        self.btn_nuevo_usuario = QPushButton("Registrar Nuevo Usuario")
        self.btn_nuevo_usuario.clicked.connect(self.abrir_registro_usuario)
        layout.addWidget(self.btn_nuevo_usuario)

        self.setLayout(layout)
        self.cargar_historias()
    
    def abrir_registro_usuario(self):
        self.ventana_registro = RegistroUsuario()
        self.ventana_registro.show()

    def cargar_historias(self):
        fecha_ini = self.fecha_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
        enfermero_id = self.combo_enfermero.currentData()

        historias = obtener_historias(fecha_ini, fecha_fin, enfermero_id)

        self.tabla.setRowCount(0)
        for row_data in historias:
            row_number = self.tabla.rowCount()
            self.tabla.insertRow(row_number)
            for col, data in enumerate(row_data):
                self.tabla.setItem(row_number, col, QTableWidgetItem(str(data)))

    def seleccionar_historia(self, row, column):
        self.historia_seleccionada = self.tabla.item(row, 0).text()

    def guardar_observacion(self):
        if not self.historia_seleccionada:
            QMessageBox.warning(self, "Error", "Seleccione una historia primero.")
            return

        texto = self.txt_observacion.toPlainText().strip()
        if not texto:
            QMessageBox.warning(self, "Error", "Ingrese una observación.")
            return

        agregar_observacion(self.historia_seleccionada, texto)
        QMessageBox.information(self, "Éxito", "Observación guardada correctamente.")
        self.txt_observacion.clear()
    
    def generar_reporte(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar reporte", "", "Excel (*.xlsx)")
        if ruta:
            exito = exportar_reporte_excel(
                fecha_inicio=self.fecha_inicio.text(),
                fecha_fin=self.fecha_fin.text(),
                usuario_id=self.combo_enfermero.currentData(),
                ruta_salida=ruta
            )
            if exito:
                QMessageBox.information(self, "Reporte", "Reporte exportado con éxito.")
            else:
                QMessageBox.warning(self, "Reporte", "No hay datos para exportar.")