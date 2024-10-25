import sys
import firebase_admin
from firebase_admin import credentials, firestore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QMessageBox, QLineEdit, QLabel, QHBoxLayout
import json
import os


def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


json_file_path = get_resource_path('service-account-credentials.json')

class DeliverersApp(QMainWindow):
    def __init__(self):
        super().__init__()

        with open(json_file_path) as json_file:
            data = json.load(json_file)
            firebase_credentials = data['firebase']

        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

        self.setWindowTitle("RTA Motoristas")
        self.setGeometry(100, 100, 600, 400)
        self.initUI()

    def initUI(self):
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Pesquisar por nome...")
        self.search_box.textChanged.connect(self.filter_table)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nome Completo", "Numero de Telefone", "Endereço"])

        self.save_button = QPushButton("Salvas Alterações")
        self.save_button.setStyleSheet("color: blue;")
        self.save_button.clicked.connect(self.save_changes)

        self.delete_button = QPushButton("Deletar Entregador")
        self.delete_button.setStyleSheet("color: red;")
        self.delete_button.clicked.connect(self.delete_deliverer)

        self.new_name_input = QLineEdit()
        self.new_name_input.setPlaceholderText("Nome Completo")
        self.new_number_input = QLineEdit()
        self.new_number_input.setPlaceholderText("Número de Telefone")
        self.new_address_input = QLineEdit()
        self.new_address_input.setPlaceholderText("Endereço")
        self.add_button = QPushButton("Adcionar Entregador")
        self.add_button.setStyleSheet("color: blue;")
        self.add_button.clicked.connect(self.add_deliverer)

        layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_box)
        
        
        search_layout.addWidget(self.save_button)
        search_layout.addWidget(self.delete_button) 
        layout.addLayout(search_layout)
        layout.addWidget(self.table)
    
        new_deliverer_layout = QHBoxLayout()
        new_deliverer_layout.addWidget(self.new_name_input)
        new_deliverer_layout.addWidget(self.new_number_input)
        new_deliverer_layout.addWidget(self.new_address_input)
        new_deliverer_layout.addWidget(self.add_button)

        layout.addLayout(new_deliverer_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_deliverers()

    def load_deliverers(self):
        doc_ref = self.db.collection('data').document('drivers')
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            self.deliverers = data['deliverer']
            self.populate_table(self.deliverers)
            self.table.setFocus()
        else:
            QMessageBox.warning(self, "Error", "Entregadores ainda não foram adicionados.")

    def populate_table(self, deliverers):
        self.table.setRowCount(len(deliverers))
        for row, deliverer in enumerate(deliverers):
            self.table.setItem(row, 0, QTableWidgetItem(deliverer['fullName']))
            self.table.setItem(row, 1, QTableWidgetItem(deliverer['mobileNumber']))
            self.table.setItem(row, 2, QTableWidgetItem(deliverer['endereco']))
        for column in range(self.table.columnCount()):
            self.table.resizeColumnToContents(column)

    def filter_table(self):
        search_text = self.search_box.text().lower()
        filtered_deliverers = [d for d in self.deliverers if search_text in d['fullName'].lower()]
        self.populate_table(filtered_deliverers)

    def add_deliverer(self):
        full_name = self.new_name_input.text().strip()
        mobile_number = self.new_number_input.text().strip()
        address = self.new_address_input.text().strip()

        if not full_name or not mobile_number or not address:
            QMessageBox.warning(self, "Input Error", "Por favor, preencha todos os campos.")
            return

        new_deliverer = {'fullName': full_name, 'mobileNumber': mobile_number, 'endereco': address}
        self.deliverers.append(new_deliverer)
        self.populate_table(self.deliverers)

        self.new_name_input.clear()
        self.new_number_input.clear()
        self.new_address_input.clear()

        QMessageBox.information(self, "Sucesso", "Novo entregador adicionado!")

    def delete_deliverer(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Erro de seleção", "Selecione um distribuidor para excluir.")
            return
        
        full_name = self.table.item(selected_row, 0).text()
        mobile_number = self.table.item(selected_row, 1).text()

        confirm = QMessageBox.question(self, "Confirmar exclusão", f"Tem certeza de que deseja excluir {full_name} com o número {mobile_number}?",
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            del self.deliverers[selected_row]
            self.populate_table(self.deliverers)
            QMessageBox.information(self, "Sucesso", "Entregador excluído com sucesso!")

    def save_changes(self):
        doc_ref = self.db.collection('data').document('drivers')   
        new_deliverers = []

        for row in range(self.table.rowCount()):
            full_name = self.table.item(row, 0).text() if self.table.item(row, 0) else ''
            mobile_number = self.table.item(row, 1).text() if self.table.item(row, 1) else ''
            address = self.table.item(row, 2).text() if self.table.item(row, 2) else ''
            new_deliverers.append({'fullName': full_name, 'mobileNumber': mobile_number, 'endereco': address})

        doc_ref.set({'deliverer': new_deliverers})
        QMessageBox.information(self, "Sucesso", "Alterações salvas com sucesso!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = DeliverersApp()
    mainWin.show()
    sys.exit(app.exec_())