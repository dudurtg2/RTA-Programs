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
import requests

import pygetwindow as gw

from firebase_admin import credentials, firestore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
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
    QScrollArea,
    QSplashScreen,
    QApplication
)

Version = "Github.com/dudurtg2 - Build 02v03a"

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
json_file_path = get_resource_path('service-account-credentials.json')
json_offline_file_path = "Developer/Data/service-account-credentials.json"

with open(json_file_path) as json_file:
    data = json.load(json_file)
    service_account_info = data['google_service_account']

# Configurações da API
API_BASE_URL = "http://carlo4664.c44.integrator.host:10500"
LOGIN_URL = f"{API_BASE_URL}/auth/login"
CIDADES_URL = f"{API_BASE_URL}/api/cidades/findAll"
ENTREGADORES_URL = f"{API_BASE_URL}/api/entregadores/findAll"
EMPRESAS_URL = f"{API_BASE_URL}/api/empresas/findAll"

# Credenciais para login na API
LOGIN_PAYLOAD = {
    "login": "carlos.e.o.savegnago@gmail.com",
    "senha": "DUdu@147"
}

# Função para obter o token de acesso
def get_access_token_and_id(login_url, payload):
    response = requests.post(login_url, json=payload)
    response.raise_for_status()
    response_data = response.json()
    
    
    access_token = response_data.get("accessToken")
    refresh_token = response_data.get("refreshToken")
    user_id = response_data.get("data", {}).get("info", {}).get("id")
    nome_id = response_data.get("data", {}).get("info", {}).get("nome")
    base_id = response_data.get("data", {}).get("info", {}).get("base", {}).get("id")
    
    return access_token, user_id, base_id, refresh_token, nome_id


def fetch_data(api_url, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()

# Obtendo o token de acesso
access_token, user_id, base_id, refresh_token, nome_id = get_access_token_and_id(LOGIN_URL, LOGIN_PAYLOAD)

# Obtendo dados das APIs
cidades_data = fetch_data(CIDADES_URL, access_token)
entregadores_data = fetch_data(ENTREGADORES_URL, access_token)
empresas_data = fetch_data(EMPRESAS_URL, access_token)

# Estruturas de dados substituindo o Firebase
LOCALES = {}
KEYS = {}
INFO_ENTERPRISE = {"EMPRESAS-SERVICO": []}
INFO_BASE = ""
BASE = []
KEY_PATH = []
CIDADES_ID_MAP = {}
EMPRESA_ID_MAP = {}
ALL_LOCALE = []
CIDADES = [] 
BASE_MAPPING = {}
INFO_DELIVERY = []

# Processando dados das cidades e bases
for cidade in cidades_data:
    regiao = cidade["regiao"]
    base = regiao["base"]
    regiao_nome = regiao["nome"]
    nome_cidade = cidade["nome"]
    id_cidade = cidade["id"]

    CIDADES.append(nome_cidade)
    CIDADES_ID_MAP[nome_cidade] = id_cidade

    if regiao_nome not in LOCALES:
        LOCALES[regiao_nome] = {
            "LOCALES": [],
            "AVAILABLEFORUPDATE": True,
            "INFO_LOCALE_REGION": regiao_nome,
            "PREFIX": regiao["prefixo"],
            "KEY_PATH": base["googledriver"]
        }

    LOCALES[regiao_nome]["LOCALES"].append(cidade["nome"])
    KEYS[base["googledriver"]] = base["googledriver"]

for regiao, data in LOCALES.items():
    locais = data.get("LOCALES", [])
    info_key = data.get("KEY_PATH")
    available_for_update = data.get("AVAILABLEFORUPDATE", False)

    BASE.append(regiao)
    KEY_PATH.append(info_key)

    BASE_MAPPING[regiao] = (
        locais,
        data.get("PREFIX"),
        KEYS.get(info_key, None),
        available_for_update
    )

    ALL_LOCALE.extend(locais)

# Processando dados das empresas
EMPRESA = [
    {
        "nome": empresa["nome"],
        "id": empresa["id"]
    }
    for empresa in empresas_data
]

# Mapeando os nomes das empresas para os IDs
EMPRESA_ID_MAP = {empresa["nome"]: empresa["id"] for empresa in EMPRESA}

INFO_ENTERPRISE["EMPRESAS-SERVICO"].extend(
    [empresa["nome"] for empresa in empresas_data]
)

# Processando entregadores
INFO_DELIVERY = [
    {
        "fullName": entregador["nome"],
        "mobileNumber": entregador["telefone"],
        "endereco": entregador["endereco"],
        "id": entregador["id"]
    }
    for entregador in entregadores_data
]

DELIVERY = [d["fullName"] for d in INFO_DELIVERY]
DELIVERY_ID = [d["id"] for d in INFO_DELIVERY]
PHONE_NUMBER = [d["mobileNumber"] for d in INFO_DELIVERY]
ADDRESSES = [d["endereco"] for d in INFO_DELIVERY]


# Configurações padrão
INFO_DEFAULT = next(iter(LOCALES.keys()), None)  # Obtém a primeira região como padrão
INFO_BASE = INFO_DEFAULT

if INFO_BASE in BASE:
    BASE.remove(INFO_BASE)
    BASE.insert(0, INFO_BASE)
BASE[1:] = sorted(BASE[1:])

KEYFOLDERDEFAULT = KEYS.get(LOCALES.get(INFO_DEFAULT, {}).get("KEY_PATH"))
AVAILABLEFORUPDATE = LOCALES.get(INFO_DEFAULT, {}).get("AVAILABLEFORUPDATE")
SELECT_CITY = LOCALES.get(INFO_DEFAULT, {}).get("LOCALES", [])
EMPRESA = INFO_ENTERPRISE.get("EMPRESAS-SERVICO", [])

SELECTMODE = False

print(AVAILABLEFORUPDATE)

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
        self.all_delivery_id = DELIVERY_ID
        
        for item, number, address, delivery_id in zip(DELIVERY, PHONE_NUMBER, ADDRESSES, DELIVERY_ID):
            checkbox = QCheckBox(item)
            checkbox.number = number
            checkbox.address = address
            checkbox.delivery_id = delivery_id
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
        global SELECT_DELIVERY_ID

        SELECT_PHONE_NUMBER = [checkbox.number for checkbox in self.checkboxes if checkbox.isChecked()]
        SELECT_DELIVERY = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
        SELECT_ADDRESS = [checkbox.address for checkbox in self.checkboxes if checkbox.isChecked()]
        SELECT_DELIVERY_ID = [checkbox.delivery_id for checkbox in self.checkboxes if checkbox.isChecked()]
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
        
        self.nome_input = QLabel()
        self.nome_input.setText(nome_id)
        self.nome_input.setStyleSheet("font-weight: bold; text-align: center;")

        self.layout_nome.addWidget(self.nome_input)

        self.layout.addLayout(self.layout_nome)
        
        self.layout_entregador = QHBoxLayout()
        self.entregador_label = QLabel("Entregador:")
        self.entregador_input = QLineEdit()

        self.layout_entregador.addWidget(self.entregador_label)
        self.layout_entregador.addWidget(self.entregador_input)
        
        self.layout_drive = QHBoxLayout()
        self.drive_label = QLabel("Entregador:")
        self.combo_box_drive = ComboBoxWithDialogDrive()

        self.layout_drive.addWidget(self.combo_box_drive)

        self.layout.addLayout(self.layout_entregador)
        self.layout.addLayout(self.layout_drive)

        self.layout_lacre = QHBoxLayout()
        self.lacre_label = QLabel("Lacre:")
        self.lacre_input = QLineEdit()


        self.layout_lacre.addWidget(self.lacre_label)
        self.layout_lacre.addWidget(self.lacre_input)

        self.layout_empresa = QHBoxLayout()
        self.empresa_label = QLabel("Empresa de bipagem:")
        self.empresa_box = QComboBox()
        self.empresa_box.addItems(EMPRESA)

        self.layout_empresa.addWidget(self.empresa_label)
        self.layout_empresa.addWidget(self.empresa_box)
        
        self.layout.addLayout(self.layout_empresa)
        
        self.layout_base = QHBoxLayout()
        self.base_label = QLabel("Região de destino:")
        self.base_combo_box = QComboBox()
        self.base_combo_box.addItems(BASE)

        self.layout_base.addWidget(self.base_label)
        self.layout_base.addWidget(self.base_combo_box)
        
        self.layout.addLayout(self.layout_base)
        self.layout.addLayout(self.layout_lacre)
         
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
        
        position_layout.addWidget(self.button1)
        
        self.layout.addLayout(position_layout)
        
        self.button2 = QPushButton("Definir Posição 2")
        self.button2.setStyleSheet("font-weight: bold; color: red;")
        
        position_layout.addWidget(self.button2)
        
        self.layout.addLayout(position_layout)

        tempo_layout = QHBoxLayout()
        
        self.layout.addLayout(tempo_layout)

        self.label_tempo1 = QLabel("Tempo de colagem:")
        self.tempo1_spinbox = QSpinBox()
        self.tempo1_spinbox.setRange(0, 5000)

        tempo_layout.addWidget(self.label_tempo1)
        tempo_layout.addWidget(self.tempo1_spinbox)

        self.label_tempo2 = QLabel("Tempo de troca:")
        self.tempo2_spinbox = QSpinBox()
        self.tempo2_spinbox.setRange(0, 5000)

        tempo_layout.addWidget(self.label_tempo2)
        tempo_layout.addWidget(self.tempo2_spinbox)

        tempo_layout_base = QHBoxLayout()

        self.layout.addLayout(tempo_layout_base)

        self.label_tempOne = QLabel("Colagem na posicão 1:")
        self.tempOne_spinbox = QSpinBox()
        self.tempOne_spinbox.setRange(1, 5)

        tempo_layout_base.addWidget(self.label_tempOne)
        tempo_layout_base.addWidget(self.tempOne_spinbox)

        self.label_tempTwo = QLabel("e posicão 2:")
        self.tempTwo_spinbox = QSpinBox()
        self.tempTwo_spinbox.setRange(0, 5)

        tempo_layout_base.addWidget(self.label_tempTwo)
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
              
        self.layout_search_label = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o codigo para buscar na lista")

        self.layout_search_label.addWidget(self.search_input)      
        
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
        
        self.reset_list_button = QPushButton("Resetar Lista")

        self.button.addWidget(self.reset_list_button)

        self.layout.addLayout(self.button)
        
        sound_layout = QHBoxLayout()
        
        self.layout.addLayout(sound_layout)
        
        self.sound_text = QLabel("Perfil de som:")
        self.sound_imput = QSpinBox()
        self.sound_imput.setRange(100, 9999)
        self.sound_temp = QSpinBox()
        self.sound_temp.setRange(150, 1500)

        sound_layout.addWidget(self.sound_text)
        sound_layout.addWidget(self.sound_imput)
        sound_layout.addWidget(self.sound_temp)

        self.ceos_label_layout = QHBoxLayout()
        self.Ceos = QLabel(Version)
        self.Ceos.setStyleSheet("color: gray;")
        self.ceos_label_layout.setAlignment(Qt.AlignRight)

        self.ceos_label_layout.addWidget(self.Ceos)
        
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

        self.base_combo_box.currentIndexChanged.connect(self.SELECT_BASE_EVENT)
        self.button1.clicked.connect(lambda: self.SET_POSITION_EVENT("pos1"))
        self.button2.clicked.connect(lambda: self.SET_POSITION_EVENT("pos2"))
        self.delete_button.clicked.connect(self.DELETE_BARCODE)
        self.search_input.textChanged.connect(self.BARCODE_SEARCH)
        self.export_button.clicked.connect(self.EXPORT_LIST)
        self.reset_list_button.clicked.connect(self.RESET_LIST)
        self.AddBarCode_input.returnPressed.connect(self.ADD_BARCODE)
        self.entry.returnPressed.connect(self.START_INSERT_EVENT)

        self.insertedBarCodes = self.LOAD_BARCODES()
        self.BARCODE_UPDATE_LIST_TABLE()

        self.MAKE_WIDGETS_VISIBLE_EVENT(self.layout_entregador, False)
        
    
             
    def MAKE_WIDGETS_VISIBLE_EVENT(self, layout, visible):
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setVisible(visible)

    def SELECT_BASE_EVENT(self, index):
        global KEYFOLDERDEFAULT, AVAILABLEFORUPDATE
        base_selecionada = self.base_combo_box.currentText()

        if base_selecionada in BASE_MAPPING:
            cidades_list, label_text, keyFolder, available = BASE_MAPPING[base_selecionada]

            KEYFOLDERDEFAULT = keyFolder
            AVAILABLEFORUPDATE = available

            self.UPDATE_CITIES_LIST(sorted(cidades_list))
            self.cidade_label.setText(label_text)

    def UPDATE_CITIES_LIST(self, listaCidades):
        global SELECT_CITY
        SELECT_CITY = listaCidades
        self.combo_box.items = listaCidades
        self.combo_box.button.setText('Click aqui para selecionar o local')

    def SET_POSITION_EVENT(self, position):
        self.currently_setting_position = position

        self.MENSAGEM_ALERT("success", "KP_a")
        
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

                if "pos1" in self.positions and "pos2" in self.positions: self.MENSAGEM_ALERT("success", "KP_a")
                else:  self.MENSAGEM_ALERT("warning", "KP_b")

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
                    self.MENSAGEM_ALERT("error", "ES_a")
                    return
                
                if len(barCode) > 55:
                    self.MENSAGEM_ALERT("error", "ES_b")
                    return

                if barCode in self.insertedBarCodes:

                    self.entry.clear()

                    ## alerta para MANUTENÇÃO
                    winsound.Beep(820, 1000)

                    self.FOCUS_WINDOWS()
                    self.MENSAGEM_ALERT("error", "ES_c")
                    return

                self.insertedBarCodes.add(barCode)
                self.BARCODE_SAVE(barCode)

                INSERT_EVENT(barCode, *self.positions["pos1"], *self.positions["pos2"], self.tempo1_spinbox.value() / 1000, self.tempo2_spinbox.value() / 1000, self.tempTwo_spinbox.value(), self.tempOne_spinbox.value())

                self.MENSAGEM_ALERT("success", "ES_d")

                self.entry.clear()

                self.SOUND_SUCCESS()
                self.FOCUS_WINDOWS()
                self.BARCODE_UPDATE_LIST_TABLE() 

            else: self.MENSAGEM_ALERT("error", "ES_e")
        else: self.MENSAGEM_ALERT("error", "ES_f")
            
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
        PDF_FILE.drawString(300, 565, "Caixas: ______ Lacre: "+self.lacre_input.text())
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


    def UPDATE_API(self, formatted_code, public_url):
        global NOME_ENTREGADOR, NUMERO_ENTREGADOR, ENDERECO_ENTREGADOR, ID_ENTREGADOR

        if SELECTMODE:
            NOME_ENTREGADOR = self.entregador_input.text()
            NUMERO_ENTREGADOR = "75900000000"
            ENDERECO_ENTREGADOR = "Endereco do entregador não definido"
        else:
            NOME_ENTREGADOR = SELECT_DELIVERY[0]
            NUMERO_ENTREGADOR = SELECT_PHONE_NUMBER[0]
            ENDERECO_ENTREGADOR = SELECT_ADDRESS[0]
            ID_ENTREGADOR = SELECT_DELIVERY_ID[0]

        if AVAILABLEFORUPDATE:
            try:
                payload = {
                    "codigoUid": formatted_code,
                    "linkDownload": public_url,
                    "empresa": EMPRESA_ID_MAP[self.empresa_box.currentText()],
                    "base": base_id,
                    "entregador": ID_ENTREGADOR,
                    "funcionario": user_id,
                    "cidade": CIDADES_ID_MAP.get(self.combo_box.button.text().split(",")[0].strip().upper(), None),
                    "codigos": [{"codigo": codigo} for codigo in self.insertedBarCodes]
                }

                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                response = requests.post("http://carlo4664.c44.integrator.host:10500/api/romaneios/save", json=payload, headers=headers)
                response.raise_for_status()  

                if response.status_code != 201:
                    QMessageBox.information(self, "Erro", f"Erro ao salvar dados: {response.text}")

            except Exception as e:
                QMessageBox.information(self, "Erro", f"Erro ao salvar dados no Firestore: {e}")
        else:
            pass

    def UPDATE_DRIVER(self, folder_date, folder_name, folder_first, folder_zero, file_path):
        try:
            credentials_drive = service_account.Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/drive"])
            drive_service = build("drive", "v3", credentials=credentials_drive)
        except Exception as e:
            QMessageBox.information(self, "Error", "Erro ao inicializar Google Drive: " + {e})
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
            print(SELECT_DELIVERY_ID[0])
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
            
            return f"https://drive.google.com/uc?id={file_id}&export=download"
        
        except Exception as e:
            QMessageBox.information(self, "Error", "Erro ao enviar arquivo para o Google Drive:\n " + {e})  
            return     

    

    def EXPORT_LIST(self):
        global AVAILABLEFORUPDATE, KEYFOLDERDEFAULT
        try:
            if (self.entregador_input.text() != "" and SELECTMODE == True) or (self.combo_box_drive.button.text() != "Click para selecionar o entregador" and SELECTMODE == False):
                if (self.nome_input.text() != ""):
                    if(self.lacre_input.text() != ""):

                        if(self.combo_box.button.text() == "Click aqui para selecionar o local"):
                            self.MENSAGEM_ALERT("error", "EL_a")
                            return
    
                        DATE_NOW = datetime.datetime.now()

                        formatted_code = DATE_NOW.strftime("RTA%Y%m%d%H%M%S%f")[:-3] + "LC"
                        formatted_now = DATE_NOW.strftime("%d-%m-%Y %H:%M:%S")
                        folder_date = DATE_NOW.strftime("%d-%m-%Y")
                        folder_name = self.combo_box.button.text().upper()
                        folder_first = self.base_combo_box.currentText().upper()
                        folder_zero = self.empresa_box.currentText().upper()

                        self.MENSAGEM_ALERT("success", "EL_b")

                        global NOME_ENTREGADOR, NUMERO_ENTREGADOR

                        if SELECTMODE:
                            NOME_ENTREGADOR = self.entregador_input.text()
                            NUMERO_ENTREGADOR = "75900000000"
                        else:
                            NOME_ENTREGADOR = SELECT_DELIVERY[0]
                            NUMERO_ENTREGADOR = SELECT_PHONE_NUMBER[0]

                        locate = ", " 

                        if self.cidade_label.text() == "Local:" or self.cidade_label.text() == "Devolução:": 
                            locate = ", Destino "

                        file_path, _ = QFileDialog.getSaveFileName(
                                self,
                                "Salvar Lista",
                                formatted_code + ", "+ self.combo_box.button.text().upper() + ", " +DATE_NOW.strftime("%d-%m-%Y"),
                                "PDF Files (*.pdf);;All Files (*)",
                                options = QFileDialog.Options(),
                            )

                        if file_path:
                            self.PDF_CREATE(file_path, formatted_now ,formatted_code).save()
                            public_url = self.UPDATE_DRIVER(folder_date, folder_name, folder_first, folder_zero, file_path)
                            self.UPDATE_API(formatted_code, public_url)

                            QMessageBox.information(self, "Sucesso", f"Romaneio salvo com sucesso.")

                            self.MENSAGEM_ALERT("success", "EL_c")

                            self.RESET_LIST()

                        else: self.MENSAGEM_ALERT("error", "EL_d")
                    else: self.MENSAGEM_ALERT("error", "EL_g")
                else: self.MENSAGEM_ALERT("error", "EL_e")
            else: self.MENSAGEM_ALERT("error", "EL_f")

        except Exception as e: 
            QMessageBox.information(self, "Error", "Erro inesperado: \n" + {e})
  
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

            self.MENSAGEM_ALERT("error", "AB_a")
            return
        if barCode:
            self.insertedBarCodes.add(barCode)
            self.BARCODE_SAVE(barCode)
            self.BARCODE_UPDATE_LIST_TABLE()
            self.SOUND_SUCCESS()
            self.AddBarCode_input.clear()
        else: 
            self.MENSAGEM_ALERT("error", "AB_b") 

    def MENSAGEM_ALERT(self, alert_type, option):
        global MENSAGEM_ALERT
        alert_messages = {
            # ADD_BARCODE mensagem ==> AB
            "AB_a": "Código de barras já inserido.",
            "AB_b": "Insira um código válido.",

            # EXPORT_LIST mensagem ==> EL
            "EL_a": "Selecione o local de destino.",
            "EL_b": "Salvando...",
            "EL_c": "Insira o proximo entregador e realize as bipagems!",
            "EL_d": "Prossiga com a bipagem normalmente.",
            "EL_e": "Por favor, defina seu nome\nantes de exportar.",
            "EL_f": "Por favor, defina o entregador\nantes de exportar.",
            "EL_g": "Por favor, defina o lacre\nantes de exportar.",

            # START_INSERT_EVENT mensagem ==> ES
            "ES_a": "Código de barras inválido. \nInsira um código com pelo menos 5 caracteres.",
            "ES_b": "Código de barras inválido. \nInsira um código com no máximo 55 caracteres.",
            "ES_c": "Código de barras já inserido.",
            "ES_d": "Código de barras inserido com sucesso.",
            "ES_e": "Por favor, defina nome e \nentregador antes de iniciar.",
            "ES_f": "Por favor, defina todas as posições antes de iniciar.",

            # keyPressEvent mensagem ==> KP
            "KP_a": "Agora realize a inserção do código de barras.",
            "KP_b": "Agora defina a próxima posição.",

            # SET_POSITION_EVENT mensagem ==> SP
            "SP_a": "Agora defina a próxima posição."
        }

        MENSAGEM_ALERT = alert_messages.get(option, "Mensagem não encontrada.")

        self.messagem.setText(MENSAGEM_ALERT)

        if alert_type == "error": self.messagem.setStyleSheet("font-weight: bold; color: red;")
        elif alert_type == "success":  self.messagem.setStyleSheet("font-weight: bold; color: blue;")
        else: self.messagem.setStyleSheet("font-weight: bold; color: orange;")


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

    splash_image = QPixmap(os.path.join(os.path.abspath("."), "loading_image.png")) 
    splash = QSplashScreen(splash_image)
    splash.show()
    
    widget = MouseCoordinateApp()
    widget.show()

    splash.finish(widget)
    sys.exit(app.exec_())
