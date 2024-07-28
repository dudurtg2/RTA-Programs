import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QSpinBox,
    QListWidget,
    QComboBox,
    QMessageBox,
    QDialog,
    QCheckBox,
    QDialogButtonBox
)
from PyQt5.QtCore import Qt

# Outras definições e dados
rota_01 = [
    "IPIRA","BAIXA GRANDE","MAIRI","VARZEA DA ROÇA","ITABERABA","IAÇU","ITATIM","CASTRO ALVES","SANTA TEREZINHA","MORRO DO CHAPEU","IRECE", "MILAGRES"
]
# ... (Outras definições de rotas)

cidades_feira = rota_01 + rota_02 + rota_03 + rota_04 + rota_05 + rota_06 + rota_07

empresa = [
    "LOGGI", "JADLOG", "SHOPEE", "ANJUN", "SEQUOIA"
]
base = [
    "FEIRA DE SANTANA", "BAIRROS DE FEIRA DE SANTANA", "ALAGOINHAS",
    "JACOBINA", "SANTO ANTONIO DE JESUS", "TRANSFERENCIA", "DEVOLUÇÃO" 
]

# Definição do ComboBoxWithDialog e MultiSelectDialog

class MultiSelectDialog(QDialog):
    def __init__(self, items):
        super().__init__()
        self.setWindowTitle('Seleção Múltipla')

        self.layout = QVBoxLayout()
        self.checkboxes = []

        for item in items:
            checkbox = QCheckBox(item)
            self.checkboxes.append(checkbox)
            self.layout.addWidget(checkbox)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def get_selected_items(self):
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

class ComboBoxWithDialog(QComboBox):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setText('Selecione opções')
        self.selected_items = []

    def mousePressEvent(self, event):
        self.open_multi_select_dialog()
        super().mousePressEvent(event)

    def open_multi_select_dialog(self):
        dialog = MultiSelectDialog(self.items)
        if dialog.exec():
            self.selected_items = dialog.get_selected_items()
            self.lineEdit().setText(', '.join(self.selected_items))

class MouseCoordinateApp(QWidget):
    def __init__(self):
        super().__init__()
        self.currently_setting_position = None
        self.setWindowTitle("Bipagem RTA")
    

        layout = QVBoxLayout()
        self.messagem = QLabel("Defina as posicoes dos mouse e aperte Enter.")
        self.messagem.setStyleSheet("font-weight: bold; color: blue;")
        layout.addWidget(self.messagem)

        self.layout_nome = QHBoxLayout()
        self.nome_label = QLabel("Nome de Funcionario:")
        self.layout_nome.addWidget(self.nome_label)
        self.nome_input = QLineEdit()
        self.layout_nome.addWidget(self.nome_input)
        layout.addLayout(self.layout_nome)

        self.layout_entregador = QHBoxLayout()
        self.entregador_label = QLabel("Nome de Entregador:")
        self.layout_entregador.addWidget(self.entregador_label)
        self.entregador_input = QLineEdit()
        self.layout_entregador.addWidget(self.entregador_input)
        
        layout.addLayout(self.layout_entregador)
        
        self.layout_empresa = QHBoxLayout()
        self.empresa_label = QLabel("Empresa de bipagem:")
        self.layout_empresa.addWidget(self.empresa_label)
        self.empresa_box = QComboBox()
        self.empresa_box.addItems(empresa)
        self.layout_empresa.addWidget(self.empresa_box)
        layout.addLayout(self.layout_empresa)
        
        self.layout_base = QHBoxLayout()
        self.base_label = QLabel("Região de destino:")
        self.layout_base.addWidget(self.base_label)
        self.base_combo_box = QComboBox()
        self.base_combo_box.addItems(base)
        self.layout_base.addWidget(self.base_combo_box)
        layout.addLayout(self.layout_base)
        self.base_combo_box.currentIndexChanged.connect(self.on_base_selected)
        
        self.layout_cidade = QHBoxLayout()
        self.cidade_label = QLabel("Cidade:")
        self.layout_cidade.addWidget(self.cidade_label)
        self.combo_box = ComboBoxWithDialog(sorted(cidades_feira))
        self.layout_cidade.addWidget(self.combo_box)
        layout.addLayout(self.layout_cidade)
        self.combo_box.currentIndexChanged.connect(self.on_cidade_selected)

        self.label = QLabel("Clique nos botões para definir a posição do mouse:")
        self.label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.label)

        position_layout = QHBoxLayout()
  
        self.button1 = QPushButton("Definir Posição 1")
        self.button1.setStyleSheet("font-weight: bold; color: red;")
        self.button1.clicked.connect(self.start_set_position1)
        position_layout.addWidget(self.button1)
        layout.addLayout(position_layout)
        
        self.button2 = QPushButton("Definir Posição 2")
        self.button2.setStyleSheet("font-weight: bold; color: red;")
        self.button2.clicked.connect(self.start_set_position2)
        position_layout.addWidget(self.button2)
        layout.addLayout(position_layout)

        tempo_layout = QHBoxLayout()
        layout.addLayout(tempo_layout)

        self.label_tempo1 = QLabel("Tempo de colagem:")
        tempo_layout.addWidget(self.label_tempo1)
        self.tempo1_spinbox = QSpinBox()
        self.tempo1_spinbox.setRange(0, 5000)
        tempo_layout.addWidget(self.tempo1_spinbox)

        self.label_tempo2 = QLabel("Tempo de troca:")
        tempo_layout.addWidget(self.label_tempo2)
        self.tempo2_spinbox = QSpinBox()
        self.tempo2_spinbox.setRange(0, 5000)
        tempo_layout.addWidget(self.tempo2_spinbox)

        tempo_layout_base = QHBoxLayout()
        layout.addLayout(tempo_layout_base)

        self.label_tempo_base = QLabel("Colagem na posicão 1:")
        tempo_layout_base.addWidget(self.label_tempo_base)
        self.tempo_base_spinbox = QSpinBox()
        self.tempo_base_spinbox.setRange(0, 5)
        tempo_layout_base.addWidget(self.tempo_base_spinbox)

        self.label_tempo_entregador = QLabel("e posicão 2:")
        tempo_layout_base.addWidget(self.label_tempo_entregador)
        self.tempo_entregador_spinbox = QSpinBox()
        self.tempo_entregador_spinbox.setRange(0, 5)
        tempo_layout_base.addWidget(self.tempo_entregador_spinbox)

        self.label = QLabel("Clique no campo abaixo para inserir os códigos:")
        self.label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.label)

        self.entry = QLineEdit()
        layout.addWidget(self.entry)

        self.counter_label = QLabel("Quantidade: 0")
        self.counter_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.counter_label)
        
        editList = QHBoxLayout()
        layout.addLayout(editList)
        
        self.delete_button = QPushButton("Delete selecionado")
        self.delete_button.setStyleSheet("color: red;")
        self.delete_button.clicked.connect(self.deletar_codigo)
        
        self.layout_search_label = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o codigo para buscar na lista")
        self.layout_search_label.addWidget(self.search_input)
        self.search_input.textChanged.connect(self.filtrar_codigos)
        
        editList.addLayout(self.layout_search_label)
        editList.addWidget(self.delete_button)

        self.codigos_list_widget = QListWidget()
        layout.addWidget(self.codigos_list_widget)

        self.adicionar_codigo_input = QLineEdit()
        self.adicionar_codigo_input.setPlaceholderText("Insira aqui manualmente o código de barras")
        layout.addWidget(self.adicionar_codigo_input)

        self.button = QHBoxLayout()
        self.export_button = QPushButton("Exportar Lista")
        self.button.addWidget(self.export_button)
        self.export_button.clicked.connect(self.exportar_lista)

        self.reset_list_button = QPushButton("Resetar Lista")
        self.button.addWidget(self.reset_list_button)
        self.reset_list_button.clicked.connect(self.resetar_lista)

        layout.addLayout(self.button)
        
        sound_layout = QHBoxLayout()
        layout.addLayout(sound_layout)
        
        self.sound_text = QLabel("Perfil de som:")
        sound_layout.addWidget(self.sound_text)
        self.sound_combobox = QComboBox()
        self.sound_combobox.addItems(["Som1", "Som2", "Som3"])
        sound_layout.addWidget(self.sound_combobox)
        
        self.sound_test_button = QPushButton("Testar som")
        sound_layout.addWidget(self.sound_test_button)

        self.setLayout(layout)
        self.show()
    
    def start_set_position1(self):
        self.currently_setting_position = 'position1'
        self.messagem.setText("Clique na posição 1 e pressione Enter")

    def start_set_position2(self):
        self.currently_setting_position = 'position2'
        self.messagem.setText("Clique na posição 2 e pressione Enter")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.set_position()
            self.messagem.setText("Defina as posicoes dos mouse e aperte Enter.")
        super().keyPressEvent(event)

    def set_position(self):
        if self.currently_setting_position == 'position1':
            self.button1.setText("Posição 1 definida")
        elif self.currently_setting_position == 'position2':
            self.button2.setText("Posição 2 definida")
        self.currently_setting_position = None

    def on_base_selected(self, index):
        print(f"Base selecionada: {self.base_combo_box.itemText(index)}")

    def on_cidade_selected(self, index):
        print(f"Cidade selecionada: {self.combo_box.currentText()}")

    def deletar_codigo(self):
        selected_item = self.codigos_list_widget.currentItem()
        if selected_item:
            self.codigos_list_widget.takeItem(self.codigos_list_widget.row(selected_item))

    def filtrar_codigos(self, text):
        for row in range(self.codigos_list_widget.count()):
            item = self.codigos_list_widget.item(row)
            item.setHidden(text not in item.text())

    def exportar_lista(self):
        codigos = [self.codigos_list_widget.item(row).text() for row in range(self.codigos_list_widget.count())]
        with open('codigos.txt', 'w') as file:
            for codigo in codigos:
                file.write(codigo + '\n')
        QMessageBox.information(self, "Exportar Lista", "Lista exportada com sucesso!")

    def resetar_lista(self):
        self.codigos_list_widget.clear()
        QMessageBox.information(self, "Resetar Lista", "Lista resetada com sucesso!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MouseCoordinateApp()
    window.show()
    sys.exit(app.exec_())
