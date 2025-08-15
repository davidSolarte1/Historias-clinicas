from PyQt5.QtWidgets import QApplication, QWidget

def centrar_ventana(widget: QWidget):
    """Centra cualquier QWidget en la pantalla principal."""
    screen = QApplication.primaryScreen().availableGeometry()
    geo = widget.frameGeometry()
    geo.moveCenter(screen.center())
    widget.move(geo.topLeft())