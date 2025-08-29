from PyQt5.QtWidgets import QApplication, QWidget
import os, sys
def centrar_ventana(widget: QWidget):
    """Centra cualquier QWidget en la pantalla principal."""
    screen = QApplication.primaryScreen().availableGeometry()
    geo = widget.frameGeometry()
    geo.moveCenter(screen.center())
    widget.move(geo.topLeft())

def ruta_recurso(ruta_relativa):
    if getattr(sys, 'frozen', False):
        # Ejecutándose como exe
        base_path = sys._MEIPASS
    else:
        # Ejecutándose como script .py
        base_path = os.path.abspath(".")
    return os.path.join(base_path, ruta_relativa)

from PyQt5.QtGui import QIcon

def aplicar_icono(ventana):
    ventana.setWindowIcon(QIcon(ruta_recurso("icons/logo.png")))