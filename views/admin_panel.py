from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QDateEdit, QTextEdit, QMessageBox, QFileDialog,
    QHeaderView 
)
from PyQt5.QtCore import QDate
from models import obtener_historias, obtener_enfermeros, agregar_observacion, exportar_reporte_excel, marcar_entregada, devolver_historia
from views.registro_usuario import RegistroUsuario
from views.observacion import ObservacionDialog
from functools import partial
import pandas as pd
from ui_utils import centrar_ventana


class AdminPanel(QWidget):
    def __init__(self, user_id, nombre):
        super().__init__()
        self.user_id = user_id
        self.nombre = nombre
        self.historia_seleccionada = None

        self.setWindowTitle(f"Panel Administrador - {self.nombre}")
        self.resize(1100, 650)
        centrar_ventana(self)

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
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Carpeta", "Cédula", "Servicio", "Fecha", "Usuario", "Estado", "Entregada", "Devolver"
        ])
        # que las columnas usen el ancho disponible
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # (opcional) filas alternadas para mejor lectura
        self.tabla.setAlternatingRowColors(True)

        self.tabla.cellClicked.connect(self.seleccionar_historia)
        layout.addWidget(self.tabla)
        
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

            # Datos normales
            for col, data in enumerate(row_data):
                self.tabla.setItem(row_number, col, QTableWidgetItem(str(data)))

            # Botón ENTREGADA
            btn_entregada = QPushButton("Aceptar")
            btn_entregada.setStyleSheet("""
                QPushButton {
                    background-color: #d4edda;     /* verde muy suave */
                    border: 1px solid #c3e6cb;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #c3e6cb;
                }
                QPushButton:pressed {
                    background-color: #b1dfbb;
                }
            """)
            btn_entregada.clicked.connect(lambda _, id_hist=row_data[0]: self.marcar_como_entregada(id_hist))
            self.tabla.setCellWidget(row_number, 7, btn_entregada)

            # Botón DEVUELTA
            btn_devuelta = QPushButton("Devolver")
            btn_devuelta.setStyleSheet("""
                QPushButton {
                    background-color: #f8d7da;     /* rojo muy suave */
                    border: 1px solid #f5c6cb;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #f5c6cb;
                }
                QPushButton:pressed {
                    background-color: #f1b0b7;
                }
            """)
            btn_devuelta.clicked.connect(lambda _, id_hist=row_data[0]: self.abrir_dialogo_observacion(id_hist))
            self.tabla.setCellWidget(row_number, 8, btn_devuelta)
    
    def abrir_dialogo_observacion(self, historia_id):
        dialogo = ObservacionDialog(historia_id, self)
        if dialogo.exec_():  # Si se guardó y cerró
            self.cargar_historias()
    
    def marcar_como_entregada(self, historia_id):
        marcar_entregada(historia_id)
        QMessageBox.information(self, "Estado", "Historia marcada como entregada.")
        self.cargar_historias()

    def devolver_historia(self, historia_id):
        texto = self.txt_observacion.toPlainText().strip()
        if not texto:
            QMessageBox.warning(self, "Error", "Ingrese una observación antes de devolver.")
            return
        devolver_historia(historia_id, texto)
        QMessageBox.information(self, "Estado", "Historia devuelta al enfermero.")
        self.txt_observacion.clear()
        self.cargar_historias()

    def seleccionar_historia(self, row, column):
        self.historia_seleccionada = self.tabla.item(row, 0).text()

    
    
    def generar_reporte(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar reporte", "", "Excel (*.xlsx)")
        if ruta:
            exito = exportar_reporte_excel(ruta_salida=ruta)
            if exito:
                QMessageBox.information(self, "Reporte", "Reporte exportado con éxito.")
            else:
                QMessageBox.warning(self, "Reporte", "No hay datos para exportar.")