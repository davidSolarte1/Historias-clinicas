from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
from models import  agregar_observacion
from ui_utils import centrar_ventana,aplicar_icono


class ObservacionDialog(QDialog):
    def __init__(self, historia_id, parent=None):
        super().__init__(parent)
        self.historia_id = historia_id
        self.setWindowTitle("Agregar Observación")
        self.setModal(True)
        self.resize(400, 300)
        centrar_ventana(self)
        aplicar_icono(self)
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Ingrese la observación para esta historia:"))
        self.txt_observacion = QTextEdit()
        layout.addWidget(self.txt_observacion)

        btn_guardar = QPushButton("Guardar Observación")
        btn_guardar.clicked.connect(self.guardar_observacion)
        layout.addWidget(btn_guardar)

        self.setLayout(layout)

    def guardar_observacion(self):
        texto = self.txt_observacion.toPlainText().strip()
        if not texto:
            QMessageBox.warning(self, "Error", "Ingrese una observación.")
            return

        agregar_observacion(self.historia_id, texto)
        QMessageBox.information(self, "Éxito", "Observación guardada correctamente.")
        #devolver_historia(self.historia_id, texto)
        self.txt_observacion.clear()
        self.accept()
