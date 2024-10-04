import os
import pathlib
import sys
import csv
import PyQt5
from PyQt5.QtCore import Qt, QDateTime   # Asegúrate de importar Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from my_ui import Ui_MainWindow  # Asegúrate de que este nombre coincida con el archivo generado
from datetime import datetime

class ImageWindow(QMainWindow):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Imagen")
        self.setGeometry(100, 100, 800, 600)  # Puedes ajustar el tamaño de la ventana

        # Añadir botones de maximizar y minimizar
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Layout para contener la imagen
        self.central_widget = PyQt5.QtWidgets.QWidget(self)  # Se necesita un widget central para QMainWindow
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)
        
        self.pixmap = QPixmap(image_path)
        if not self.pixmap.isNull():
             self.update_image()  # Actualizar la imagen para que se ajuste al tamaño de la ventana
        else:
            QMessageBox.warning(self, "Error", f"No se pudo cargar la imagen en la ruta: {image_path}")

        # Habilitar el redimensionamiento
        self.setMinimumSize(200, 200)
        self.resize(800, 600)
    

    def resizeEvent(self, event):
        self.update_image()
        super().resizeEvent(event)

    def update_image(self):
        # Escalar la imagen para que ocupe el tamaño máximo dentro de la ventana, manteniendo la proporción
        if not self.pixmap.isNull():
            scaled_pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Conectar los botones para cambiar de página en el QStackedWidget
        self.ui.Historial_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.Camara_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        
        script_dir = pathlib.Path(__file__).parent.absolute()
        csv_file = os.path.join(script_dir, '../../detections.csv')
        # Cargar el contenido del CSV en la tabla cuando se selecciona la página de "Historial"
        self.load_csv(csv_file)

        # Conectar los QDateTimeEdit al método de filtrado
        self.ui.before_dateTimeEdit.setDateTime(QDateTime.currentDateTime())  # Establece la fecha actual como predeterminada
        self.ui.after_dateTimeEdit_2.setDateTime(QDateTime.currentDateTime())  # Establece la fecha actual como predeterminada
        self.ui.before_dateTimeEdit.dateTimeChanged.connect(self.filtrar_por_fecha)
        self.ui.after_dateTimeEdit_2.dateTimeChanged.connect(self.filtrar_por_fecha)

        # Conectar el evento de clic en la celda con la función que abre la imagen
        self.ui.tableWidget.cellDoubleClicked.connect(self.mostrar_imagen)


    def load_csv(self, filename):
        # Crear la tabla en la primera página del stackedWidget
        tableWidget = self.ui.tableWidget

         # Establecer el modo de redimensionamiento para que las columnas ocupen todo el espacio disponible
        tableWidget.horizontalHeader().setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.Stretch)

        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # Suponiendo que la primera fila es de encabezados
            tableWidget.setColumnCount(len(headers))
            tableWidget.setHorizontalHeaderLabels(headers)

            for row_idx, row in enumerate(reader):
                tableWidget.insertRow(row_idx)
                for col_idx, item in enumerate(row):
                    if col_idx == 0:  # Si es la primera columna (donde se supone que están las fechas)
                        try:
                            # Convertir y formatear la fecha
                            fecha_objeto = datetime.strptime(item, "%Y%m%d_%H%M%S")
                            item = fecha_objeto.strftime("%d/%m/%Y %H:%M:%S")
                        except ValueError:
                            pass  # En caso de que la fecha no esté en el formato esperado, se deja como está

                    table_item = QTableWidgetItem(item)
                    table_item.setTextAlignment(Qt.AlignCenter)  # Centrar el texto
                    tableWidget.setItem(row_idx, col_idx, table_item)

    def filtrar_por_fecha(self):
        # Obtener las fechas seleccionadas
        fecha_inicio = self.ui.before_dateTimeEdit.dateTime().toPyDateTime()
        fecha_fin = self.ui.after_dateTimeEdit_2.dateTime().toPyDateTime()

        # Recorrer la tabla y filtrar las filas
        for row in range(self.ui.tableWidget.rowCount()):
            fecha_item = self.ui.tableWidget.item(row, 0)  # Obtener el elemento en la primera columna
            if fecha_item:
                fecha_texto = fecha_item.text()  # Obtener el texto del elemento
                fecha_tabla = datetime.strptime(fecha_texto, "%d/%m/%Y %H:%M:%S")

                if fecha_inicio <= fecha_tabla <= fecha_fin:
                    self.ui.tableWidget.showRow(row)
                else:
                    self.ui.tableWidget.hideRow(row)

    def mostrar_imagen(self, row, column):
            # Suponiendo que la ruta de la imagen está en la última columna
            image_path = self.ui.tableWidget.item(row, column).text()
            if os.path.exists(image_path):
                self.image_window = ImageWindow(image_path)
                self.image_window.show()
            else:
                QMessageBox.warning(self, "Error", f"La ruta de la imagen no es válida: {image_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
