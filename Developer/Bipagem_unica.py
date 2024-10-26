import datetime
import sys
import json
import pyautogui
import pyperclip
import time
import winsound
import os
import qrcode
import io
import firebase_admin

import pygetwindow as gw

from firebase_admin import credentials, firestore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

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
    QFileDialog,
    QComboBox,
    QMessageBox,
    QCheckBox,
    QDialogButtonBox,
    QDialog,
    QScrollArea
)

Version = "Github.com/dudurtg2 - Digital Versão 2.2"

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

with open("Data/service-account-credentials.json") as json_file:
    data = json.load(json_file)
    service_account_info = data['google_service_account']
    firebase_credentials = data['firebase']

firebase_admin.initialize_app(credentials.Certificate(firebase_credentials))
db = firestore.client()

LOCALES = db.collection('data').document('InfoLocales').get().to_dict()
CITY_ALG = LOCALES.get("ALG", [])
CITY_JAC = LOCALES.get("JAC", [])
CITY_SAJ = LOCALES.get("SAJ", [])
CITY_FSA = LOCALES.get("FSA", [])
CITY_SAJ_bairros = LOCALES.get("JAC_bairros", [])
CITY_FSA_bairros = LOCALES.get("FSA_bairros", [])
CITY_ALG_bairros = LOCALES.get("ALG_bairros", [])
CITY_JAC_bairros = LOCALES.get("JAC_bairros", [])
DEVOLUCAO = LOCALES.get("DEVOLUCAO", [])
TRANSFERENCIA = LOCALES.get("TRANSFERENCIA", [])

INFO = db.collection('data').document('InfoBase').get().to_dict()
EMPRESA = INFO.get("EMPRESAS-SERVICO", [])
BASE = INFO.get("BASE", [])

KEYS = db.collection('data').document('KeyFolderDrive').get().to_dict()
KEY_FSA = KEYS.get("KEYS_FSA")
KEY_ALG = KEYS.get("KEYS_ALG")
KEY_SAJ = KEYS.get("KEYS_SAJ")
KEY_JAC = KEYS.get("KEYS_JAC")
KEY_DEV = KEYS.get("KEYS_DEV")

SELECT_CITY = CITY_FSA
ALL_LOCALE = CITY_FSA_bairros + CITY_ALG_bairros + CITY_JAC_bairros + CITY_FSA + CITY_ALG + CITY_JAC + CITY_SAJ + CITY_SAJ_bairros + DEVOLUCAO + TRANSFERENCIA

KEYFOLDERDEFAULT = KEY_FSA
SELECTMODE = False
AVAILABLEFORUPDATE = False

def fetch_deliverers():
    DOC = db.collection('data').document('InfoDriver').get()

    if DOC.exists:
        data = DOC.to_dict()
        DELIVERY = [d['fullName'] for d in data['deliverer']]
        PHONE_NUMBER = [d['mobileNumber'] for d in data['deliverer']]
        ADDRESSES = [d['endereco'] for d in data['deliverer']]
        return DELIVERY, PHONE_NUMBER, ADDRESSES
    else:
        return [], [], []

DELIVERY, PHONE_NUMBER, ADDRESSES = fetch_deliverers()

class MultiSelectDialog(QDialog):
    def __init__(self, items):
        super().__init__()
        self.setWindowTitle('Local')

        self.layout = QVBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Pesquisar...')
        self.search_box.textChanged.connect(self.filter_items)
        self.layout.addWidget(self.search_box)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        
        self.checkboxes = []
        self.all_items = items 
        
        for item in items:
            checkbox = QCheckBox(item)
            self.checkboxes.append(checkbox)
            self.scroll_layout.addWidget(checkbox)
        
        self.layout.addWidget(self.scroll_area)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)
        
        self.setLayout(self.layout)
    
    def filter_items(self):
        filter_text = self.search_box.text().lower()
        for checkbox in self.checkboxes:
            checkbox.setVisible(filter_text in checkbox.text().lower())
    
    def get_selected_items(self):
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

class ComboBoxWithDialog(QWidget):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items
        
        self.layout = QHBoxLayout()
        self.button = QPushButton('Click aqui para selecionar o local')
        self.button.setStyleSheet("font-weight: bold; color: blue;")
        self.button.clicked.connect(self.open_multi_select_dialog)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        
        self.selected_items = []

    def open_multi_select_dialog(self):
        dialog = MultiSelectDialog(self.items)
        if dialog.exec():
            self.selected_items = dialog.get_selected_items()
            if not self.selected_items:  
                self.button.setText('Click aqui para selecionar o local')
            else:
                self.button.setText(', '.join(self.selected_items))                
        
class MultiSelectDialogDrive(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Entregadores')

        self.layout = QVBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Pesquisar...')
        self.search_box.textChanged.connect(self.filter_items)
        self.layout.addWidget(self.search_box)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.checkboxes = []
        self.all_items = DELIVERY
        self.all_numbers = PHONE_NUMBER
        self.all_addresses = ADDRESSES
        
        for item, number, address in zip(DELIVERY, PHONE_NUMBER, ADDRESSES):
            checkbox = QCheckBox(item)
            checkbox.number = number
            checkbox.address = address
            checkbox.stateChanged.connect(self.uncheck_others)
            self.checkboxes.append(checkbox)
            self.scroll_layout.addWidget(checkbox)

        self.layout.addWidget(self.scroll_area)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def filter_items(self, text):
        for checkbox in self.checkboxes:
            checkbox.setVisible(text.lower() in checkbox.text().lower())

    def uncheck_others(self, state):
        if state == Qt.Checked:
            sender = self.sender()
            for checkbox in self.checkboxes:
                if checkbox != sender:
                    checkbox.setChecked(False)

    def get_selected_items(self):
        global SELECT_DELIVERY
        global SELECT_PHONE_NUMBER
        global SELECT_ADDRESS

        SELECT_PHONE_NUMBER = [checkbox.number for checkbox in self.checkboxes if checkbox.isChecked()]
        SELECT_DELIVERY = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
        SELECT_ADDRESS = [checkbox.address for checkbox in self.checkboxes if checkbox.isChecked()]
        return SELECT_DELIVERY

class ComboBoxWithDialogDrive(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QHBoxLayout()
        self.button = QPushButton('Click para selecionar o entregador')
        self.button.setStyleSheet("font-weight: bold; color: blue;")
        self.button.clicked.connect(self.open_multi_select_dialog_Drive)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        
        self.selected_item = None

    def open_multi_select_dialog_Drive(self):
        dialog = MultiSelectDialogDrive()
        if dialog.exec():
            selected_items = dialog.get_selected_items()
            if not selected_items:  
                self.button.setText('Click para selecionar o entregador')
            else:
                self.selected_item = selected_items[0]
                self.button.setText(self.selected_item)
            
        
class MouseCoordinateApp(QWidget):
    def __init__(self):
        super().__init__()
        global SELECT_CITY
        
        self.currently_setting_position = None
        self.setWindowTitle("Bipagem RTA")

        self.layout = QVBoxLayout()

        self.is_entregador_visible = True
        
        self.messagem = QLabel("Defina as posicoes dos mouse e aperte Enter.")
        self.messagem.setStyleSheet("font-weight: bold; color: blue;")
        
        self.layout.addWidget(self.messagem)

        self.layout_nome = QHBoxLayout()
        self.nome_label = QLabel("Funcionario:")
        self.layout_nome.addWidget(self.nome_label)
        self.nome_input = QLineEdit()
        self.layout_nome.addWidget(self.nome_input)

        self.botao_liga_desliga = QPushButton("Digitar", self)
        self.botao_liga_desliga.clicked.connect(self.TOGGLE_BUTTON_EVENT)

        self.layout_nome.addWidget(self.botao_liga_desliga)
        
        self.layout.addLayout(self.layout_nome)
        
        self.layout_entregador = QHBoxLayout()
        self.entregador_label = QLabel("Entregador:")
        self.layout_entregador.addWidget(self.entregador_label)
        self.entregador_input = QLineEdit()
        self.layout_entregador.addWidget(self.entregador_input)
        
        self.layout_drive = QHBoxLayout()
        self.drive_label = QLabel("Entregador:")
        self.combo_box_drive = ComboBoxWithDialogDrive()
        self.layout_drive.addWidget(self.combo_box_drive)

        self.layout.addLayout(self.layout_entregador)
    
        self.layout.addLayout(self.layout_drive)

        self.layout_empresa = QHBoxLayout()
        self.empresa_label = QLabel("Empresa de bipagem:")
        self.layout_empresa.addWidget(self.empresa_label)
        self.empresa_box = QComboBox()
        self.empresa_box.addItems(EMPRESA)
        self.layout_empresa.addWidget(self.empresa_box)
        
        self.layout.addLayout(self.layout_empresa)
        
        self.layout_base = QHBoxLayout()
        self.base_label = QLabel("Região de destino:")
        self.layout_base.addWidget(self.base_label)
        self.base_combo_box = QComboBox()
        self.base_combo_box.addItems(BASE)
        self.layout_base.addWidget(self.base_combo_box)
        
        self.layout.addLayout(self.layout_base)
        self.base_combo_box.currentIndexChanged.connect(self.SELECT_BASE_EVENT)
        
        self.layout_cidade = QHBoxLayout()
        self.cidade_label = QLabel("Cidade:")
        self.combo_box = ComboBoxWithDialog(sorted(SELECT_CITY))
        self.layout_cidade.addWidget(self.combo_box)
        
        self.layout.addLayout(self.layout_cidade)

        self.label = QLabel("Clique nos botões para definir a posição do mouse:")
        self.label.setStyleSheet("font-weight: bold;")
        
        self.layout.addWidget(self.label)

        position_layout = QHBoxLayout()
        self.button1 = QPushButton("Definir Posição 1")
        self.button1.setStyleSheet("font-weight: bold; color: red;")
        self.button1.clicked.connect(lambda: self.SET_POSITION_EVENT("pos1"))
        position_layout.addWidget(self.button1)
        
        self.layout.addLayout(position_layout)
        
        self.button2 = QPushButton("Definir Posição 2")
        self.button2.setStyleSheet("font-weight: bold; color: red;")
        self.button2.clicked.connect(lambda: self.SET_POSITION_EVENT("pos2"))
        position_layout.addWidget(self.button2)
        
        self.layout.addLayout(position_layout)

        tempo_layout = QHBoxLayout()
        
        self.layout.addLayout(tempo_layout)

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
        
        self.layout.addLayout(tempo_layout_base)

        self.label_tempOne = QLabel("Colagem na posicão 1:")
        tempo_layout_base.addWidget(self.label_tempOne)
        self.tempOne_spinbox = QSpinBox()
        self.tempOne_spinbox.setRange(1, 5)
        tempo_layout_base.addWidget(self.tempOne_spinbox)

        self.label_tempTwo = QLabel("e posicão 2:")
        tempo_layout_base.addWidget(self.label_tempTwo)
        self.tempTwo_spinbox = QSpinBox()
        self.tempTwo_spinbox.setRange(0, 5)
        tempo_layout_base.addWidget(self.tempTwo_spinbox)

        self.label = QLabel("Clique no campo abaixo para inserir os códigos:")
        self.label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.label)

        self.entry = QLineEdit()
        self.layout.addWidget(self.entry)

        self.counter_label = QLabel("Quantidade: 0")
        self.counter_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.counter_label)
        
        editList = QHBoxLayout()
        
        self.layout.addLayout(editList)
        
        self.delete_button = QPushButton("Delete selecionado")
        self.delete_button.setStyleSheet("color: red;")
        self.delete_button.clicked.connect(self.DELETE_BARCODE)
        
        self.layout_search_label = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o codigo para buscar na lista")
        self.layout_search_label.addWidget(self.search_input)
        self.search_input.textChanged.connect(self.BARCODE_SEARCH)
        
        editList.addLayout(self.layout_search_label)
        editList.addWidget(self.delete_button)

        self.codigos_list_widget = QListWidget()
        self.layout.addWidget(self.codigos_list_widget)

        self.AddBarCode_input = QLineEdit()
        self.AddBarCode_input.setPlaceholderText("Insira aqui manualmente o código de barras")
        self.layout.addWidget(self.AddBarCode_input)

        self.button = QHBoxLayout()
        self.export_button = QPushButton("Exportar Lista")
        self.button.addWidget(self.export_button)
        self.export_button.clicked.connect(self.EXPORT_LIST)

        self.reset_list_button = QPushButton("Resetar Lista")
        self.button.addWidget(self.reset_list_button)
        self.reset_list_button.clicked.connect(self.RESET_LIST)

        self.layout.addLayout(self.button)
        
        sound_layout = QHBoxLayout()
        
        self.layout.addLayout(sound_layout)
        
        self.sound_text = QLabel("Perfil de som:")
        sound_layout.addWidget(self.sound_text)
        self.sound_imput = QSpinBox()
        self.sound_imput.setRange(100, 9999)
        self.sound_temp = QSpinBox()
        self.sound_temp.setRange(150, 1500)
        sound_layout.addWidget(self.sound_imput)
        sound_layout.addWidget(self.sound_temp)

        self.ceos_label_layout = QHBoxLayout()
        self.Ceos = QLabel(Version)
        self.Ceos.setStyleSheet("color: gray;")
        self.ceos_label_layout.addWidget(self.Ceos)
        self.ceos_label_layout.setAlignment(Qt.AlignRight)
        
        self.layout.addLayout(self.ceos_label_layout)

        self.setLayout(self.layout)
        
        self.tempTwo_spinbox.setValue(1)
        self.tempOne_spinbox.setValue(1)
        self.tempo2_spinbox.setValue(20)
        self.tempo1_spinbox.setValue(20)
        self.sound_temp.setValue(150)
        self.sound_imput.setValue(1530)
        self.positions = {}
        self.counter = 0
        self.AddBarCode_input.returnPressed.connect(self.ADD_BARCODE)
        self.entry.returnPressed.connect(self.START_INSERT_EVENT)
        self.insertedBarCodes = self.LOAD_BARCODES()
        self.BARCODE_UPDATE_LIST_TABLE()

        self.MAKE_WIDGETS_VISIBLE_EVENT(self.layout_entregador, False)

    def TOGGLE_BUTTON_EVENT(self):
        global SELECTMODE
        SELECTMODE = not SELECTMODE
    
        if SELECTMODE:
            print(SELECTMODE)
            self.botao_liga_desliga.setText("Selecionar")
            self.MAKE_WIDGETS_VISIBLE_EVENT(self.layout_entregador, True)
            self.MAKE_WIDGETS_VISIBLE_EVENT(self.layout_drive, False)
            self.is_entregador_visible = True 
        else:
            print(SELECTMODE)
            self.botao_liga_desliga.setText("Digitar")
            self.MAKE_WIDGETS_VISIBLE_EVENT(self.layout_entregador, not self.is_entregador_visible)
            self.MAKE_WIDGETS_VISIBLE_EVENT(self.layout_drive, self.is_entregador_visible)
            self.is_entregador_visible = not self.is_entregador_visible 
             
    def MAKE_WIDGETS_VISIBLE_EVENT(self, layout, visible):
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setVisible(visible)

    def SELECT_BASE_EVENT(self, index):
        global KEYFOLDERDEFAULT, AVAILABLEFORUPDATE
        base_selecionada = self.base_combo_box.currentText()

        base_mapping = {
            "ALAGOINHAS": (CITY_ALG, "Cidade:", KEY_ALG, True),
            "JACOBINA": (CITY_JAC, "Cidade:", KEY_JAC, True),
            "SANTO ANTONIO DE JESUS": (CITY_SAJ, "Cidade:" , KEY_SAJ, True),
            "FEIRA DE SANTANA": (CITY_FSA, "Cidade:", KEY_FSA, True),

            "DEVOLUÇÃO": (DEVOLUCAO, "Devolução:", KEY_DEV, True),
            "TRANSFERENCIA": (TRANSFERENCIA, "Local:", KEY_DEV, True),

            "BAIRROS DE FEIRA DE SANTANA": (CITY_FSA_bairros, "Bairros:", KEY_FSA, False),
            "BAIRROS DE ALAGOINHAS": (CITY_ALG_bairros, "Bairros:", KEY_ALG, False),
            "BAIRROS DE S. A. DE JESUS": (CITY_SAJ_bairros, "Bairros:", KEY_SAJ, False),
            "BAIRROS DE JACOBINA": (CITY_SAJ_bairros, "Bairros:", KEY_JAC, False),

            "TODOS AS LOCALIDADES": (ALL_LOCALE, "Bairros, Cidades, Locais:", KEY_FSA, True),
        }
        
        if base_selecionada in base_mapping:
            cidades_list, label_text, keyFolder, AVAILABLE = base_mapping[base_selecionada]

            KEYFOLDERDEFAULT = keyFolder
            AVAILABLEFORUPDATE = AVAILABLE

            self.UPDATE_CITIES_LIST(sorted(cidades_list))
            self.cidade_label.setText(label_text)

    def UPDATE_CITIES_LIST(self, listaCidades):
        global SELECT_CITY
        SELECT_CITY = listaCidades
        self.combo_box.items = listaCidades
        self.combo_box.button.setText('Click aqui para selecionar o local')

    def SET_POSITION_EVENT(self, position):
        self.messagem.setText("Posicione o mouse e pressione Enter.")
        self.messagem.setStyleSheet("font-weight: bold; color: blue;")
        self.currently_setting_position = position

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.currently_setting_position:
                x, y = pyautogui.position()
                self.positions[self.currently_setting_position] = (x, y)
                if self.currently_setting_position == 'pos1':
                    self.button1.setText(f"Posição 1: ({x}, {y})")
                    self.button1.setStyleSheet("font-weight: bold; color: blue;")
                elif self.currently_setting_position == 'pos2':
                    self.button2.setText(f"Posição 2: ({x}, {y})")
                    self.button2.setStyleSheet("font-weight: bold; color: blue;")
                self.currently_setting_position = None
                if "pos1" in self.positions and "pos2" in self.positions:
                    self.messagem.setText("Agora realize a inserção do código de barras.")
                    self.messagem.setStyleSheet("font-weight: bold; color: blue;")
                else:
                    self.messagem.setText("Agora defina a proxima posição.")
                    self.messagem.setStyleSheet("font-weight: bold; color: red;")

    def LOAD_BARCODES(self):
        insertedBarCodes = set()
        if os.path.exists("insertedBarCodes.txt"):
            with open("insertedBarCodes.txt", "r") as file:
                for linha in file:
                    linha = linha.strip()
                    if linha: insertedBarCodes.add(linha)
        return insertedBarCodes

    def BARCODE_SAVE(self, codigo):
        with open("insertedBarCodes.txt", "a") as file:
            if not file.tell(): file.write("\n")
            file.write(f"{codigo}\n")

    def BARCODE_UPDATE_LIST_TABLE(self):
        self.codigos_list_widget.clear()
        self.codigos_list_widget.addItems(self.insertedBarCodes)
        if self.insertedBarCodes: self.counter = len(self.insertedBarCodes)
        else: self.counter = 0
        self.counter_label.setText(f"Quantidade: {self.counter}")

    def SOUND_SUCCESS(self): 
        winsound.Beep(int(self.sound_imput.value()) , int(self.sound_temp.value()))
        
    def START_INSERT_EVENT(self):
        if ("pos1" in self.positions and "pos2" in self.positions):
            if (self.entregador_input.text() != "" and SELECTMODE == True) or (self.combo_box_drive.button.text() != "Click para selecionar o entregador" and SELECTMODE == False):
                barCode = self.entry.text()
                if len(barCode) < 5:
                    self.messagem.setText( "Código de barras inválido. \nInsira um código com pelo menos 5 caractere." )
                    self.messagem.setStyleSheet("font-weight: bold; color: red;")
                    return
                if len(barCode) > 55:
                    self.messagem.setText( "Código de barras inválido. \nInsira um código com no maximo 55 caractere." )
                    self.messagem.setStyleSheet("font-weight: bold; color: red;")
                    return

                if barCode in self.insertedBarCodes:
                    self.entry.clear()
                    self.FOCUS_WINDOWS()
                    winsound.Beep(820, 1000)
                    self.messagem.setText("Código de barras já inserido.")
                    self.messagem.setStyleSheet("font-weight: bold; color: red;")
                    return

                self.insertedBarCodes.add(barCode)
                self.BARCODE_SAVE(barCode)

                INSERT_EVENT(barCode, *self.positions["pos1"], *self.positions["pos2"], self.tempo1_spinbox.value() / 1000, self.tempo2_spinbox.value() / 1000, self.tempTwo_spinbox.value(), self.tempOne_spinbox.value())

                self.messagem.setText(f"Codigo de barras inserido com sucesso.")
                self.messagem.setStyleSheet("font-weight: bold; color: blue;")

                self.entry.clear()
                self.SOUND_SUCCESS()
                self.FOCUS_WINDOWS()
                self.BARCODE_UPDATE_LIST_TABLE() 
            else: 
                self.messagem.setText( "Por favor, defina nome e \nentregador antes de iniciar." )
                self.messagem.setStyleSheet("font-weight: bold; color: red;")
        else: 
            self.messagem.setText( "Por favor, defina todas as posições antes de iniciar." )
            self.messagem.setStyleSheet("font-weight: bold; color: red;")
            
    def FOCUS_WINDOWS(self):
        window = gw.getWindowsWithTitle(self.windowTitle())[0]
        if window: window.activate()

    def PDF_CREATE(self, file_path,formatted_now, formatted_code):
        PDF_FILE = canvas.Canvas(file_path, pagesize=letter)

        default_font_size = 12
        signature_font_size = 16
        title_font_size = 18

        PDF_FILE.setFont("Helvetica-Bold", title_font_size)

        PDF_FILE.line(70, 765, 540, 765)
        PDF_FILE.line(70, 625, 540, 625)

        PDF_FILE.setFont("Helvetica", default_font_size)
        PDF_FILE.drawString(70, 750, "Codigo de ficha: " + formatted_code)
        PDF_FILE.drawString(70, 735, "Empresa de serviços: " + self.empresa_box.currentText())
        PDF_FILE.drawString(70, 720, "Funcionario: " + self.nome_input.text())
        if SELECTMODE:
            PDF_FILE.drawString(70, 705, "Entregador: " + self.entregador_input.text())
        else:
            PDF_FILE.drawString(70, 705, "Entregador: " + SELECT_DELIVERY[0])

        PDF_FILE.drawString(70, 690, self.counter_label.text())
        PDF_FILE.drawString(70, 675, "Dia e hora da bipagem: " + formatted_now)
        PDF_FILE.drawString(70, 660, "Região: " + self.base_combo_box.currentText())

        if not SELECTMODE:
            PDF_FILE.drawString(70, 645, "Numero do entregador: (" + SELECT_PHONE_NUMBER[0] + ")")
        else:
            PDF_FILE.drawString(70, 645, "Numero do entregador: (00000000000)")

        PDF_FILE.setFont("Helvetica", signature_font_size)
        PDF_FILE.drawString(70, 630, "Assinatura: ____________________________ Data: __/__/____")
        PDF_FILE.setFont("Helvetica", default_font_size)

        PDF_FILE.drawString(70, 610, self.cidade_label.text() + " " + self.combo_box.button.text().upper())
        if not SELECTMODE:
            
            PDF_FILE.drawString(70, 585, "End: " + SELECT_ADDRESS[0])
        else:
            PDF_FILE.drawString(70, 585, "End: Endereco do entregador não definido")
        
        PDF_FILE.setFont("Helvetica", signature_font_size)
        PDF_FILE.drawString(300, 565, "Caixas: ______    Sacas: ______")
        PDF_FILE.drawString(70, 565, "Codigos inseridos:")

        PDF_FILE.setFont("Helvetica", default_font_size)

        qr_data = formatted_code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=25,
            border=1,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        qr_buffer = io.BytesIO()
        img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        PDF_FILE.drawImage(ImageReader(qr_buffer), 430, 650, 110, 110)

        y = 550
        for codigo in self.insertedBarCodes:
            if y < 50:
                PDF_FILE.showPage()
                y = 750
            PDF_FILE.drawString(70, y, str(codigo))
            y -= 12

        return PDF_FILE

    def UPDATE_DRIVER(self, folder_date, folder_name, folder_first, folder_zero, file_path):
        try:
            credentials_drive = service_account.Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/drive"])
            drive_service = build("drive", "v3", credentials=credentials_drive)
        except Exception as e:
            self.messagem.setText(f"Erro ao inicializar Google Drive: {e}")
            self.messagem.setStyleSheet("font-weight: bold; color: red;")
            return
        def find_or_create_folder(folder_name, parent_id=None):
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            response = drive_service.files().list(
                q=query,
                spaces="drive",
                fields="files(id, name)",
            ).execute()
            files = response.get("files", [])
            if files:
                return files[0]["id"]
            else:
                folder_metadata = {
                    "name": folder_name,
                    "mimeType": "application/vnd.google-apps.folder",
                }
                if parent_id:
                    folder_metadata["parents"] = [parent_id]
                folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
                return folder["id"]

        try:
            main_folder_id = find_or_create_folder(folder_date, KEYFOLDERDEFAULT)
            folder_zero_id = find_or_create_folder(folder_zero, main_folder_id)

            folder_prefixes = {
                "Bairros:": "",
                "Local:": "TRANSFERENCIA PARA ",
                "Devolução:": "DEVOLUÇÃO PARA ",
            }

            prefix = folder_prefixes.get(self.cidade_label.text(), "INTERIOR DE ")

            first_subfolder_id = find_or_create_folder(prefix + folder_first, folder_zero_id)
            second_subfolder_id = find_or_create_folder(folder_name, first_subfolder_id)

            file_metadata = {
                "name": os.path.basename(file_path),
                "mimeType": "application/pdf",
                "supportsAllDrives": True,
                "visibility": "public", 
                "parents": [second_subfolder_id],
            }

            media = MediaFileUpload(file_path, mimetype="application/pdf")
            uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

            file_id = uploaded_file.get('id')

            permission = {
                'role': 'reader',
                'type': 'anyone',
            }
            drive_service.permissions().create(fileId=file_id, body=permission).execute()
            public_url = f"https://drive.google.com/uc?id={file_id}&export=download"

            return public_url
        except Exception as e:
            self.messagem.setText(f"Erro ao enviar arquivo para o Google Drive:\n {e}")
            self.messagem.setStyleSheet("font-weight: bold; color: red;")
            return     

    def UPDATE_FIREBASE(self, formatted_code, formatted_now, public_url):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(firebase_credentials)
                firebase_admin.initialize_app(cred)
                
            db = firestore.client()

        except Exception as e:
            self.messagem.setText(f"Erro ao inicializar Firebase: {e}")
            self.messagem.setStyleSheet("font-weight: bold; color: red;")
            return
        
        if AVAILABLEFORUPDATE:
            try:   
                db.collection('bipagem').document(formatted_code).set({
                    'Empresa': self.empresa_box.currentText(),
                    'Funcionario': self.nome_input.text(),
                    'Entregador': self.entregador_input.text(),
                    'Local': self.combo_box.button.text().upper(),
                    'Codigo_de_ficha': formatted_code,
                    'Hora_e_Dia': formatted_now,
                    'Quantidade': self.counter_label.text(),
                    'Inicio': "aguardando",
                    'Fim': "aguardando",
                    'Status': "aguardando",
                    'Motorista': "aguardando",
                    'Codigos inseridos': self.insertedBarCodes,
                    'Download_link': public_url
                })

            except Exception as e:
                self.messagem.setText(f"Erro ao salvar dados no Firestore: {e}")
                self.messagem.setStyleSheet("font-weight: bold; color: red;")
                return
        else:
            pass

    def EXPORT_LIST(self):
        global AVAILABLEFORUPDATE, KEYFOLDERDEFAULT
        try:
            if (self.entregador_input.text() != "" and SELECTMODE == True) or (self.combo_box_drive.button.text() != "Click para selecionar o entregador" and SELECTMODE == False):
                if (self.nome_input.text() != ""):

                    if(self.combo_box.button.text() == "Click aqui para selecionar o local"):
                        self.messagem.setText(f"Selecione o local de destino.")
                        self.messagem.setStyleSheet("font-weight: bold; color: red;")
                        return
                    
                    options = QFileDialog.Options()

                    DATE_NOW = datetime.datetime.now()

                    formatted_code = DATE_NOW.strftime("RTA%Y%m%d%H%M%S%f")[:-3] + "LC"
                    formatted_now = DATE_NOW.strftime("%d-%m-%Y %H:%M:%S")
                    folder_date = DATE_NOW.strftime("%d-%m-%Y")
                    folder_name = self.combo_box.button.text().upper()
                    folder_first = self.base_combo_box.currentText().upper()
                    folder_zero = self.empresa_box.currentText().upper()

                    self.messagem.setText(f"Salvando...")
                    self.messagem.setStyleSheet("font-weight: bold; color: blue;")

                    locate = ", Entregador "

                    if self.cidade_label.text() == "Local:" or self.cidade_label.text() == "Devolução:":
                        locate = ", Destino "

                    file_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "Salvar Lista",
                        formatted_code + locate + self.entregador_input.text().upper() + ", " +DATE_NOW.strftime("%d-%m-%Y"),
                        "PDF Files (*.pdf);;All Files (*)",
                        options=options,
                    )
                    if file_path:
                        
                        self.PDF_CREATE(file_path, formatted_now ,formatted_code).save()
                        public_url = self.UPDATE_DRIVER(folder_date, folder_name, folder_first, folder_zero, file_path)
                        self.UPDATE_FIREBASE(formatted_code, formatted_now, public_url)

                        QMessageBox.information(self, "Sucesso", f"Romaneio salvo com sucesso.")
                        self.messagem.setText(f"Insira o proximo entregador e realize as bipagems!")
                        self.messagem.setStyleSheet("font-weight: bold; color: blue;")

                        self.RESET_LIST()

                    else:
                        self.messagem.setText(f"Prossiga com a bipagem normalmente.")
                        self.messagem.setStyleSheet("font-weight: bold; color: blue;")
                else:
                    self.messagem.setText("Por favor, defina seu nome\nantes de exportar.")
                    self.messagem.setStyleSheet("font-weight: bold; color: red;")
            else:
                self.messagem.setText("Por favor, defina o entregador\nantes de exportar.")
                self.messagem.setStyleSheet("font-weight: bold; color: red;")
        except Exception as e:
            self.messagem.setText(f"Erro inesperado: {e}")
            self.messagem.setStyleSheet("font-weight: bold; color: red;")
  
    def RESET_LIST(self):
        self.insertedBarCodes.clear()
        if not self.cidade_label.text() == "Local:":
            self.entregador_input.clear()
            self.combo_box_drive.button.setText("Click aqui para selecionar o entregador")

        if os.path.exists("insertedBarCodes.txt"): os.remove("insertedBarCodes.txt")
        self.BARCODE_UPDATE_LIST_TABLE()

    def DELETE_BARCODE(self):
        selected_items = self.codigos_list_widget.selectedItems()
        if not selected_items: return
        for item in selected_items:
            codigo = item.text()
            self.insertedBarCodes.remove(codigo)
            self.codigos_list_widget.takeItem(self.codigos_list_widget.row(item))
            self.counter -= 1
            self.counter_label.setText(f"Quantidade: {self.counter}")
        self.SAVE_BARCODES()
        self.search_input.clear()

    def SAVE_BARCODES(self):
        with open("insertedBarCodes.txt", "w") as file:
            for codigo in self.insertedBarCodes:
                file.write(f"{codigo}\n")

    def BARCODE_SEARCH(self):
        search_term = self.search_input.text().lower()
        self.codigos_list_widget.clear()
        for codigo in self.insertedBarCodes:
            if search_term in codigo.lower(): self.codigos_list_widget.addItem(codigo)

    def ADD_BARCODE(self):
        barCode = self.AddBarCode_input.text()
        if barCode in self.insertedBarCodes:
            self.AddBarCode_input.clear()
            self.FOCUS_WINDOWS()
            winsound.Beep(820, 1000)
            self.messagem.setText("Código de barras já inserido.")
            self.messagem.setStyleSheet("font-weight: bold; color: red;")
            return
        if barCode:
            self.insertedBarCodes.add(barCode)
            self.BARCODE_SAVE(barCode)
            self.BARCODE_UPDATE_LIST_TABLE()
            self.SOUND_SUCCESS()
            self.AddBarCode_input.clear()
        else: 
            self.messagem.setText("Insira um código válido.")
            self.messagem.setStyleSheet("font-weight: bold; color: red;")

def INSERT_EVENT(barCode, x, y, x2, y2, tempo1, tempo2, tempTwo, tempOne):
    positionOne = [(x, y)] * tempOne
    positionTwo = [(x2, y2)] * tempTwo
    positions = {
        "positions1": {f"field{i+1}": coord for i, coord in enumerate(positionOne)},
        "positions2": {f"field{i+1}": coord for i, coord in enumerate(positionTwo)},
    }
    pyperclip.copy(barCode)
    for positions, fields in positions.items():
        for field, coordinates in fields.items():
            pyautogui.moveTo(*coordinates, duration=0)
            pyautogui.click()
            pyautogui.hotkey("ctrl", "v")
            time.sleep(tempo1)
            pyautogui.press("enter")
            time.sleep(20 / 1000)
            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("backspace")
            time.sleep(20 / 1000)
        time.sleep(tempo2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MouseCoordinateApp()
    widget.show()
    sys.exit(app.exec_())
