import sys
from PyQt5.QtWidgets import QApplication
from database import create_tables, seed_admin
from views.login import LoginWindow

if __name__ == "__main__":
    create_tables()
    seed_admin()

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
    