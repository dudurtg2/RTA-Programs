import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal

class Switch(QFrame):
    checkedChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(66, 22)

        self.setStyleSheet("""
            QFrame {
                background-color: #ccc;
                border-radius: 11px;
            }
            QFrame[checked=true] {
                background-color: #6DDA6B;
            }
            QFrame[checked=false] {
                background-color: #E15B52;
            }
        """)

        self.checked = False

    def mousePressEvent(self, event):
        self.setChecked(not self.checked)

    def setChecked(self, checked):
        self.checked = checked
        self.setProperty("checked", str(checked).lower())
        self.style().unpolish(self)
        self.style().polish(self)
        self.checkedChanged.emit(checked)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Controle de Salvamento MySQL")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.switch = Switch()
        self.switch.checkedChanged.connect(self.toggle_mysql_save)

        self.lbl_status = QLabel("Desligado", alignment=Qt.AlignCenter)

        layout.addWidget(self.lbl_status)
        layout.addWidget(self.switch)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.mysql_connected = False

    def toggle_mysql_save(self, checked):
        self.mysql_connected = checked
        if checked:
            self.lbl_status.setText("Ligado")
            # Lógica para ligar o salvamento no MySQL aqui
        else:
            self.lbl_status.setText("Desligado")
            # Lógica para desligar o salvamento no MySQL aqui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
