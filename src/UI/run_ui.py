import os
import sys

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from other_util_classes import verifier

import PyQt5
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from my_ui import Ui_MainWindow 
from datetime import datetime

class ImageWindow(QMainWindow):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Imagen")
        self.setGeometry(100, 100, 800, 600)

        self.setWindowFlags(
            Qt.Window
            | Qt.WindowCloseButtonHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint)

        # Layout for the image
        self.central_widget = PyQt5.QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)
        
        self.pixmap = QPixmap(image_path)
        if not self.pixmap.isNull():
             self.update_image()
        else:
            QMessageBox.warning(self, "Error", f"No se pudo cargar la imagen en la ruta: {image_path}")

        # Allowing resize
        self.setMinimumSize(200, 200)
        self.resize(800, 600)
    

    def resizeEvent(self, event):
        self.update_image()
        super().resizeEvent(event)

    def update_image(self):
        if not self.pixmap.isNull():
            scaled_pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connecting the buttons to change page of the stacked widget
        self.ui.Historial_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.Camara_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        
        self.load_history()

        # Conectar los QDateTimeEdit al método de filtrado
        self.ui.before_dateTimeEdit.setDateTime(QDateTime.currentDateTime())  # Set current time as placeholder
        self.ui.after_dateTimeEdit_2.setDateTime(QDateTime.currentDateTime())  # Same 
        
        self.ui.before_dateTimeEdit.dateTimeChanged.connect(self.filter_by_date)
        self.ui.after_dateTimeEdit_2.dateTimeChanged.connect(self.filter_by_date)

        # Conectar el evento de clic en la celda con la función que abre la imagen
        self.ui.tableWidget.cellDoubleClicked.connect(self.show_image)


    def load_history(self):
        """
        Loads the detection history from the CSV file into the QTableWidget.
        Uses the get_history function to retrieve the data.
        """
        # Create the table in the first page of the stackedWidget
        tableWidget = self.ui.tableWidget

        # Set the resize mode so that columns occupy the available space
        tableWidget.horizontalHeader().setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.Stretch)

        # Get the history data
        history = verifier.get_history()

        # If history is empty, clear the table and exit
        if not history:
            tableWidget.setRowCount(0)
            tableWidget.setColumnCount(0)
            return

        # Obtain headers from the keys of the first record
        headers = list(history[0].keys())
        tableWidget.setColumnCount(len(headers))
        tableWidget.setHorizontalHeaderLabels(headers)

        # Populate the table with history data
        tableWidget.setRowCount(len(history))
        for row_idx, record in enumerate(history):
            for col_idx, header in enumerate(headers):
                item = record[header]
                
                # Format the timestamp if it is the first column
                if header == 'Timestamp':  # Check if the header is 'Timestamp'
                    try:
                        # Convert and format the date
                        date_object = datetime.strptime(item, "%Y%m%d_%H%M%S")
                        item = date_object.strftime("%d/%m/%Y %H:%M:%S")
                    except ValueError:
                        pass  # If the date is not in the expected format, leave it as is

                table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignCenter)  # Center the text
                tableWidget.setItem(row_idx, col_idx, table_item)


    def filter_by_date(self):
        # Obtener las fechas seleccionadas Obtain the selected dates
        fecha_inicio = self.ui.before_dateTimeEdit.dateTime().toPyDateTime()
        fecha_fin = self.ui.after_dateTimeEdit_2.dateTime().toPyDateTime()

        # Iterate through the table and filter the rows
        for row in range(self.ui.tableWidget.rowCount()):
            fecha_item = self.ui.tableWidget.item(row, 0)  # Obtener el elemento en la primera columna
            if fecha_item:
                fecha_texto = fecha_item.text()  # Obtener el texto del elemento
                fecha_tabla = datetime.strptime(fecha_texto, "%d/%m/%Y %H:%M:%S")

                if fecha_inicio <= fecha_tabla <= fecha_fin:
                    self.ui.tableWidget.showRow(row)
                else:
                    self.ui.tableWidget.hideRow(row)

    def show_image(self, row):
        """
        Shows the image in a new window when a table cell is double-clicked.
        Assumes the image path is in the last column of the table.
        """
        # Get the image path from the last column
        image_path_item = self.ui.tableWidget.item(row, self.ui.tableWidget.columnCount() - 1)
        if image_path_item:
            image_path = image_path_item.text()
            if os.path.exists(image_path):
                self.image_window = ImageWindow(image_path)
                self.image_window.show()
            else:
                QMessageBox.warning(self, "Error", f"The image path is invalid: {image_path}")
        else:
            QMessageBox.warning(self, "Error", "No image path found in the selected row.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
