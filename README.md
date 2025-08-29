Aplicación para digitalizar el proceso de recepción de historias clinicas.

Tener en cuenta la versión de mysql-connector-python==8.0.33

Para empaquetar la app ejecutar:

pyinstaller --noconfirm --noconsole --clean --name SIREH --add-data "icons;icons" --collect-all mysql.connector --hidden-import mysql.connector --hidden-import mysql.connector.locales.eng.client_error --collect-all openpyxl --collect-all pandas main.py

