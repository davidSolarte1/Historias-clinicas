from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QToolButton,
    QTableWidget, QTableWidgetItem, QComboBox, QDateEdit, QTextEdit, QMessageBox, QFileDialog,
    QHeaderView 
)
from datetime import date
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDate,Qt, QSize
from models import obtener_historias, obtener_enfermeros, exportar_reporte_excel, marcar_entregada, obtener_servicios,obtener_historia_por_id, eliminar_historia
from views.registro_usuario import RegistroUsuario
from views.editar_usuario import EditarUsuario
from views.observacion import ObservacionDialog
from functools import partial
import pandas as pd
from ui_utils import centrar_ventana,ruta_recurso, aplicar_icono


class AdminPanel(QWidget):
    def __init__(self, user_id, nombre):
        super().__init__()
        self.user_id = user_id
        self.nombre = nombre
        self.historia_seleccionada = None
        aplicar_icono(self)
        self.setWindowTitle(f"SIREH - {self.nombre}")
        self.resize(1400, 650)
        centrar_ventana(self)

        layout = QVBoxLayout()

        # Filtros
        filtros_layout = QHBoxLayout()

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDate(QDate.currentDate())
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
        
        # Servicio/Área
        self.combo_servicio = QComboBox()
        self.combo_servicio.addItem("Todos")
        try:
            for s in obtener_servicios():
                if s:
                    self.combo_servicio.addItem(s)
        except:
            pass  # si falla, queda solo "Todos"
        filtros_layout.addWidget(QLabel("Área/Servicio:"))
        filtros_layout.addWidget(self.combo_servicio)

        # Estado
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Todos", "registrada", "devuelta", "revisada", "entregada"])
        filtros_layout.addWidget(QLabel("Estado:"))
        filtros_layout.addWidget(self.combo_estado)

        self.btn_buscar = QToolButton()
        self.btn_buscar.setText("Buscar")
        self.btn_buscar.setIcon(QIcon(ruta_recurso("icons/buscar.png")))
        self.btn_buscar.setIconSize(QSize(48, 48)) 
        self.btn_buscar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_buscar.setFixedSize(80, 80)
        self.btn_buscar.clicked.connect(self.cargar_historias)
        filtros_layout.addWidget(self.btn_buscar)

        layout.addLayout(filtros_layout)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(14)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Carpeta", "Cédula","Nombre", "Apellido", "Servicio", "Fecha", "Usuario", "Estado", "Fecha Devolución", "Nueva Entrega", "Aceptar", "Devolver", "Eliminar"
        ])
        # que las columnas usen el ancho disponible
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # (opcional) filas alternadas para mejor lectura
        self.tabla.setAlternatingRowColors(True)

        self.tabla.cellClicked.connect(self.seleccionar_historia)
        layout.addWidget(self.tabla)
        
        #Botones
        acciones_layout = QHBoxLayout()
        #Exportar a EXCEL
        self.btn_exportar_excel = QToolButton()
        self.btn_exportar_excel.setText("Exportar a Excel")
        self.btn_exportar_excel.setIcon(QIcon(ruta_recurso("icons/excel.png")))
        self.btn_exportar_excel.setIconSize(QSize(48, 48)) 
        self.btn_exportar_excel.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_exportar_excel.clicked.connect(self.generar_reporte)
        acciones_layout.addWidget(self.btn_exportar_excel)

        #Registrar Usuarios
        self.btn_nuevo_usuario = QToolButton()
        self.btn_nuevo_usuario.setText("Registrar Nuevo Usuario")
        self.btn_nuevo_usuario.setIcon(QIcon(ruta_recurso("icons/nuevo_usuario.png")))
        self.btn_nuevo_usuario.setIconSize(QSize(48, 48)) 
        self.btn_nuevo_usuario.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_nuevo_usuario.clicked.connect(self.abrir_registro_usuario)
        acciones_layout.addWidget(self.btn_nuevo_usuario)

        #Editar Usuarios
        self.btn_editar_usuario = QToolButton()
        self.btn_editar_usuario.setText("Editar Usuario")
        self.btn_editar_usuario.setIcon(QIcon(ruta_recurso("icons/editar_usuario.png")))
        self.btn_editar_usuario.setIconSize(QSize(48, 48)) 
        self.btn_editar_usuario.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_editar_usuario.clicked.connect(self.abrir_editar_usuario)
        acciones_layout.addWidget(self.btn_editar_usuario)

        #Cerrar Sesion
        self.btn_cerrar = QToolButton()
        self.btn_cerrar.setText("Salir")
        self.btn_cerrar.setIcon(QIcon(ruta_recurso("icons/cerrar-sesion.png")))
        self.btn_cerrar.setIconSize(QSize(48, 48)) 
        self.btn_cerrar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_cerrar.clicked.connect(self.cerrar_sesion)
        self.btn_cerrar.setFixedWidth(80)
        acciones_layout.addWidget(self.btn_cerrar)


        layout.addLayout(acciones_layout)
        self.setLayout(layout)
        self.cargar_historias()
    
    def abrir_registro_usuario(self):
        self.ventana_registro = RegistroUsuario()
        self.ventana_registro.show()
    
    def abrir_editar_usuario(self):
        self.ventana_editar = EditarUsuario()
        self.ventana_editar.show()

    def cargar_historias(self):
        fecha_ini = self.fecha_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
        enfermero_id = self.combo_enfermero.currentData()
        servicio = self.combo_servicio.currentText()
        estado = self.combo_estado.currentText()

        historias = obtener_historias(fecha_ini, fecha_fin, enfermero_id, servicio, estado)

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
            btn_entregada.setCursor(Qt.PointingHandCursor)
            btn_entregada.clicked.connect(lambda _, id_hist=row_data[0]: self.marcar_como_entregada(id_hist))
            self.tabla.setCellWidget(row_number, 11, btn_entregada)
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
            btn_devuelta.setCursor(Qt.PointingHandCursor)
            btn_devuelta.clicked.connect(lambda _, id_hist=row_data[0]: self.abrir_dialogo_observacion(id_hist))
            self.tabla.setCellWidget(row_number, 12, btn_devuelta)
            
            # Botón ELIMINAR
            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background-color: #e57373;     /* rojo suave */
                    border: 1px solid #d32f2f;
                    color: white;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #ef5350;
                }
                QPushButton:pressed {
                    background-color: #c62828;
                }
                QPushButton:disabled {
                    background-color: #bdbdbd;     /* gris cuando está deshabilitado */
                    border: 1px solid #ABABAB;
                    color: #757575;
                }
            """)
            btn_eliminar.setCursor(Qt.PointingHandCursor)
            if row_data[8] == "entregada":  
                btn_eliminar.setEnabled(False)

            btn_eliminar.clicked.connect(lambda _, id_hist=row_data[0]: self.confirmacion_eliminar(id_hist))
            self.tabla.setCellWidget(row_number, 13, btn_eliminar)
    
    def abrir_dialogo_observacion(self, historia_id):
        dialogo = ObservacionDialog(historia_id, self)
        if dialogo.exec_():  # Si se guardó y cerró
            self.cargar_historias()
    
    def marcar_como_entregada(self, historia_id):
        marcar_entregada(historia_id)
        QMessageBox.information(self, "Estado", "Historia marcada como entregada.")
        self.cargar_historias()

    def confirmacion_eliminar(self, historia_id: int):
        # Consultar datos de la historia
        row = obtener_historia_por_id(historia_id)
        if not row:
            QMessageBox.critical(self, "Error", "No se encontró la historia.")
            return

        _, num, ced, nom, ape, srv, fecha, *_ = row

        detalle = f"""
        Carpeta: {num}
        Paciente: {nom} {ape}
        Cédula: {ced}
        Servicio: {srv}
        Fecha: {fecha}
        """

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Confirmar eliminación")
        msg.setText(f"¿Está seguro de eliminar esta historia?\n\n{detalle}\n\nEsta acción no se puede deshacer.")

        # Botones personalizados en español
        btn_si = msg.addButton("Sí", QMessageBox.YesRole)
        btn_no = msg.addButton("No", QMessageBox.NoRole)

        # Hacemos que "No" sea el predeterminado
        msg.setDefaultButton(btn_no)

        msg.exec_()

        if msg.clickedButton() == btn_si:
            try:
                ok = eliminar_historia(historia_id)
                if ok:
                    QMessageBox.information(self, "Eliminada", "La historia fue eliminada correctamente.")
                    self.cargar_historias()
                else:
                    QMessageBox.warning(self, "Aviso", "No se pudo eliminar (verifique el ID).")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")


    def seleccionar_historia(self, row, column):
        self.historia_seleccionada = self.tabla.item(row, 0).text()

    
    
    def generar_reporte(self):
        nombre_archivo = f"Reporte_{date.today().isoformat()}.xlsx"
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar reporte", nombre_archivo, "Excel (*.xlsx)")
        if ruta:
            exito = exportar_reporte_excel(ruta_salida=ruta)
            if exito:
                QMessageBox.information(self, "Reporte", "Reporte exportado con éxito.")
            else:
                QMessageBox.warning(self, "Reporte", "No hay datos para exportar.")

    def cerrar_sesion(self):
        from views.login import LoginWindow
        self.close()
        self.login = LoginWindow()
        self.login.show()