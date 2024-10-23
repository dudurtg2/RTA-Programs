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

json_file_path = 'Data/data.json'

with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

rota_01 = data.get("rota_01", [])
rota_02 = data.get("rota_02", [])
rota_03 = data.get("rota_03", [])
rota_04 = data.get("rota_04", [])
rota_05 = data.get("rota_05", [])
rota_06 = data.get("rota_06", [])
rota_07 = data.get("rota_07", [])

cidades_algoinhas = data.get("cidades_algoinhas", [])
cidades_jacobina = data.get("cidades_jacobina", [])
cidades_saj = data.get("cidades_saj", [])
cidades_feira = rota_01 + rota_02 + rota_03 + rota_04 + rota_05 + rota_06 + rota_07

barrios_saj = data.get("barrios_saj", [])
barrios_feria = data.get("barrios_feria", [])
barrios_alagoinhas = data.get("barrios_alagoinhas", [])
barrios_jacobina = data.get("barrios_jacobina", [])

devolucaos = data.get("devolucaos", [])
empresa = data.get("empresa", [])
base = data.get("base", [])
tranferencia = data.get("tranferencia", [])

allLocate = barrios_feria + barrios_alagoinhas + barrios_jacobina + cidades_feira + cidades_algoinhas + cidades_jacobina + cidades_saj + barrios_saj + devolucaos + tranferencia

rota_dict = {city: '001' for city in rota_01}
rota_dict.update({city: '002' for city in rota_02})
rota_dict.update({city: '003' for city in rota_03})
rota_dict.update({city: '004' for city in rota_04})
rota_dict.update({city: '005' for city in rota_05})
rota_dict.update({city: '006' for city in rota_06})
rota_dict.update({city: '008' for city in tranferencia})

keyFolderFSA = data.get("KEYS_FSA")
keyFolderALG = data.get("KEYS_ALG")
keyFolderSAJ = data.get("KEYS_SAJ")
keyFolderJAC = data.get("KEYS_JAC")
keyFolderDEV = data.get("KEYS_DEV")

keyFolderDefault = keyFolderFSA

print(keyFolderDefault)
print(keyFolderFSA)
print(keyFolderALG)
print(keyFolderSAJ)
print(keyFolderJAC)
print(keyFolderDEV)

cidades = cidades_feira

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
        global rota
        if self.selected_items:
            selected_cidade = self.selected_items[0].upper() 
            rota = rota_dict.get(selected_cidade, 'base')
        else:
            rota = 'base'


class MouseCoordinateApp(QWidget):
    def __init__(self):
        super().__init__()
        
        global cidades
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
        self.combo_box = ComboBoxWithDialog(sorted(cidades))
        self.layout_cidade.addWidget(self.combo_box)
        
        layout.addLayout(self.layout_cidade)

        self.label = QLabel("Clique nos botões para definir a posição do mouse:")
        self.label.setStyleSheet("font-weight: bold;")
        
        layout.addWidget(self.label)

        position_layout = QHBoxLayout()
        self.button1 = QPushButton("Definir Posição 1")
        self.button1.setStyleSheet("font-weight: bold; color: red;")
        self.button1.clicked.connect(lambda: self.start_set_position("pos1"))
        position_layout.addWidget(self.button1)
        
        layout.addLayout(position_layout)
        
        self.button2 = QPushButton("Definir Posição 2")
        self.button2.setStyleSheet("font-weight: bold; color: red;")
        self.button2.clicked.connect(lambda: self.start_set_position("pos2"))
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
        self.delete_button.clicked.connect(self.DeleteBarCode)
        
        self.layout_search_label = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o codigo para buscar na lista")
        self.layout_search_label.addWidget(self.search_input)
        self.search_input.textChanged.connect(self.FilterBarCodes)
        
        editList.addLayout(self.layout_search_label)
        editList.addWidget(self.delete_button)

        self.codigos_list_widget = QListWidget()
        layout.addWidget(self.codigos_list_widget)

        self.AddBarCode_input = QLineEdit()
        self.AddBarCode_input.setPlaceholderText("Insira aqui manualmente o código de barras")
        layout.addWidget(self.AddBarCode_input)

        self.button = QHBoxLayout()
        self.export_button = QPushButton("Exportar Lista")
        self.button.addWidget(self.export_button)
        self.export_button.clicked.connect(self.ExportList)

        self.reset_list_button = QPushButton("Resetar Lista")
        self.button.addWidget(self.reset_list_button)
        self.reset_list_button.clicked.connect(self.ResetList)

        layout.addLayout(self.button)
        
        sound_layout = QHBoxLayout()
        
        layout.addLayout(sound_layout)
        
        self.sound_text = QLabel("Perfil de som:")
        sound_layout.addWidget(self.sound_text)
        self.sound_imput = QSpinBox()
        self.sound_imput.setRange(100, 9999)
        self.sound_temp = QSpinBox()
        self.sound_temp.setRange(150, 1500)
        sound_layout.addWidget(self.sound_imput)
        sound_layout.addWidget(self.sound_temp)

        self.ceos_label_layout = QHBoxLayout()
        self.Ceos = QLabel("Github.com/dudurtg2 - Versão 1.10.1")
        self.Ceos.setStyleSheet("color: gray;")
        self.ceos_label_layout.addWidget(self.Ceos)
        self.ceos_label_layout.setAlignment(Qt.AlignRight)
        
        layout.addLayout(self.ceos_label_layout)

        self.setLayout(layout)
        
        self.tempTwo_spinbox.setValue(1)
        self.tempOne_spinbox.setValue(1)
        self.tempo2_spinbox.setValue(20)
        self.tempo1_spinbox.setValue(20)
        self.sound_temp.setValue(150)
        self.sound_imput.setValue(1530)
        self.positions = {}
        self.counter = 0
        self.AddBarCode_input.returnPressed.connect(self.AddBarCode)
        self.entry.returnPressed.connect(self.StartInsertBarCode)
        self.insertedBarCodes = self.carregar_insertedBarCodes()
        self.UpdateBarCodeListWidget()
        
    
    def on_base_selected(self, index):
        base_selecionada = self.base_combo_box.currentText()
        global keyFolderDefault

        base_mapping = {
            "ALAGOINHAS": (cidades_algoinhas, "Cidade:", keyFolderALG),
            "JACOBINA": (cidades_jacobina, "Cidade:", keyFolderJAC),
            "SANTO ANTONIO DE JESUS": (cidades_saj, "Cidade:" , keyFolderSAJ),
            "FEIRA DE SANTANA": (cidades_feira, "Cidade:", keyFolderFSA),
            "DEVOLUÇÃO": (devolucaos, "Devolução:", keyFolderDEV),
            "TRANSFERENCIA": (tranferencia, "Local:", keyFolderDEV),
            "BAIRROS DE FEIRA DE SANTANA": (barrios_feria, "Bairros:", keyFolderFSA),
            "BAIRROS DE ALAGOINHAS": (barrios_alagoinhas, "Bairros:", keyFolderALG),
            "BAIRROS DE S. A. DE JESUS": (barrios_saj, "Bairros:", keyFolderSAJ),
            "BAIRROS DE JACOBINA": (barrios_saj, "Bairros:", keyFolderJAC),
            "TODOS AS LOCALIDADES": (allLocate, "Bairros, Cidades, Locais:", keyFolderFSA),
        }
        
        if base_selecionada in base_mapping:
            cidades_list, label_text, keyFolder = base_mapping[base_selecionada]

            keyFolderDefault = keyFolder

            self.atualizar_cidades(sorted(cidades_list))
            self.cidade_label.setText(label_text)

    def atualizar_cidades(self, lista_cidades):
        global cidades
        cidades = lista_cidades
        self.combo_box.items = lista_cidades
        self.combo_box.button.setText('Click aqui para selecionar o local')

    def start_set_position(self, position):
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

    def carregar_insertedBarCodes(self):
        insertedBarCodes = set()
        if os.path.exists("insertedBarCodes.txt"):
            with open("insertedBarCodes.txt", "r") as file:
                for linha in file:
                    linha = linha.strip()
                    if linha: insertedBarCodes.add(linha)
        return insertedBarCodes

    def SaveBarCode(self, codigo):
        with open("insertedBarCodes.txt", "a") as file:
            if not file.tell(): file.write("\n")
            file.write(f"{codigo}\n")

    def UpdateBarCodeListWidget(self):
        self.codigos_list_widget.clear()
        self.codigos_list_widget.addItems(self.insertedBarCodes)
        if self.insertedBarCodes: self.counter = len(self.insertedBarCodes)
        else: self.counter = 0
        self.counter_label.setText(f"Quantidade: {self.counter}")

    def sound_success(self): 
        winsound.Beep(int(self.sound_imput.value()) , int(self.sound_temp.value()))
        
    def StartInsertBarCode(self):
        if ( "pos1" in self.positions and "pos2" in self.positions and self.nome_input.text() != "" and self.entregador_input.text() != ""):
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
                self.bring_to_front()
                winsound.Beep(820, 1000)
                self.messagem.setText("Código de barras já inserido.")
                self.messagem.setStyleSheet("font-weight: bold; color: red;")
                return

            self.insertedBarCodes.add(barCode)
            self.SaveBarCode(barCode)
            
            InsertBarCode(barCode, *self.positions["pos1"], *self.positions["pos2"], self.tempo1_spinbox.value() / 1000, self.tempo2_spinbox.value() / 1000, self.tempTwo_spinbox.value(), self.tempOne_spinbox.value())
            
            self.messagem.setText(f"Codigo de barras inserido com sucesso.")
            self.messagem.setStyleSheet("font-weight: bold; color: blue;")
            
            self.entry.clear()
            self.sound_success()
            self.bring_to_front()
            self.UpdateBarCodeListWidget() 
        else: 
            self.messagem.setText( "Por favor, defina todas as posições, nome e \nentregador antes de iniciar." )
            self.messagem.setStyleSheet("font-weight: bold; color: red;")
            
    def bring_to_front(self):
        window = gw.getWindowsWithTitle(self.windowTitle())[0]
        if window: window.activate()
            
    def ExportList(self):
        global rota
        try:
            if (self.nome_input.text() != "" and self.entregador_input.text() != ""):
                if(self.combo_box.button.text() == "Click aqui para selecionar o local"):
                    self.messagem.setText(f"Selecione o local de destino.")
                    self.messagem.setStyleSheet("font-weight: bold; color: red;")
                    return
                options = QFileDialog.Options()
                now = datetime.datetime.now()
                formatted_code = now.strftime("RTA%Y%m%d%H%M%S%f")[:-3] + "LC"
                self.messagem.setText(f"Salvando...")
                self.messagem.setStyleSheet("font-weight: bold; color: blue;")
                locate = ", Entregador "
                if self.cidade_label.text() == "Local:" or self.cidade_label.text() == "Devolução:":
                    locate = ", Destino "
                
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Salvar Lista",
                    formatted_code + locate + self.entregador_input.text().upper() + ", " +now.strftime("%d-%m-%Y"),
                    "PDF Files (*.pdf);;All Files (*)",
                    options=options,
                )
                if file_path:
                    c = canvas.Canvas(file_path, pagesize=letter)
                    now = datetime.datetime.now()
                    formatted_now = now.strftime("%d-%m-%Y %H:%M:%S")
                    folder_date = now.strftime("%d-%m-%Y")
                    folder_name = self.combo_box.button.text().upper()
                    folder_first = self.base_combo_box.currentText().upper()
                    folder_zero = self.empresa_box.currentText().upper()
                    
                    default_font_size = 12
                    signature_font_size = 16
                    title_font_size = 18

                    c.setFont("Helvetica-Bold", title_font_size)

                    c.line(70, 765, 540, 765)
                    c.line(70, 630, 540, 630)

                    c.setFont("Helvetica", default_font_size)
                    c.drawString(70, 750, "Codigo de ficha: " + formatted_code)
                    c.drawString(70, 735, "Empresa de serviços: " + self.empresa_box.currentText())
                    c.drawString(70, 720, "Funcionario: " + self.nome_input.text())
                    c.drawString(70, 705, "Entregador: " + self.entregador_input.text())
                    c.drawString(70, 690, self.counter_label.text())
                    c.drawString(70, 675, "Dia e hora da bipagem: " + formatted_now)
                    c.drawString(70, 660, "Região: " + self.base_combo_box.currentText())
                    c.setFont("Helvetica", signature_font_size)
                    c.drawString(70, 635, "Assinatura: ____________________________ Data: __/__/____")
                    c.setFont("Helvetica", default_font_size)

                    c.drawString(70, 605, self.cidade_label.text() + " " + self.combo_box.button.text().upper())
                    
                    c.setFont("Helvetica", signature_font_size)
                    c.drawString(300, 585, "Caixas: ______    Sacas: ______")
                    c.drawString(70, 585, "Codigos inseridos:")

                    c.setFont("Helvetica", default_font_size)

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

                    c.drawImage(ImageReader(qr_buffer), 430, 650, 110, 110)

                    y = 570
                    for codigo in self.insertedBarCodes:
                        if y < 50:
                            c.showPage()
                            y = 750
                        c.drawString(70, y, str(codigo))
                        y -= 12

                    c.save()
                    
                    try:
                        with open('Data/service-account-credentials.json') as json_file:
                            data = json.load(json_file)
                            service_account_info = data['google_service_account']
                            firebase_credentials = data['firebase']
                    except Exception as e:
                        self.messagem.setText(f"Erro ao carregar credenciais: {e}")
                        self.messagem.setStyleSheet("font-weight: bold; color: red;")
                        return

                    try:
                        if not firebase_admin._apps:
                            cred = credentials.Certificate(firebase_credentials)
                            firebase_admin.initialize_app(cred)

                        db = firestore.client()
                    except Exception as e:
                        self.messagem.setText(f"Erro ao inicializar Firebase: {e}")
                        self.messagem.setStyleSheet("font-weight: bold; color: red;")
                        return

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
                        
                    global keyFolderDefault

                    try:
                        main_folder_id = find_or_create_folder(folder_date, keyFolderDefault)
                        folder_zero_id = find_or_create_folder(folder_zero, main_folder_id)
                        
                        if self.cidade_label.text() == "Bairros:":
                            first_subfolder_id = find_or_create_folder(folder_first, folder_zero_id)
                            second_subfolder_id = find_or_create_folder(folder_name, first_subfolder_id)
                        elif self.cidade_label.text() == "Local:":
                            first_subfolder_id = find_or_create_folder("TRANSFERENCIA PARA " + folder_first, folder_zero_id)
                            second_subfolder_id = find_or_create_folder(folder_name, first_subfolder_id)
                        elif self.cidade_label.text() == "Devolução:":
                            first_subfolder_id = find_or_create_folder("DEVOLUÇÃO PARA " + folder_first, folder_zero_id)
                            second_subfolder_id = find_or_create_folder(folder_name, first_subfolder_id)
                        else:
                            first_subfolder_id = find_or_create_folder("INTERIOR DE " + folder_first, folder_zero_id)
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
                    except Exception as e:
                        self.messagem.setText(f"Erro ao enviar arquivo para o Google Drive:\n {e}")
                        self.messagem.setStyleSheet("font-weight: bold; color: red;")
                        return

                    try:
                        if rota == None:
                            rota = 'base'
                        if rota != "base":
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
                                'Rota': rota,
                                'Download_link': public_url
                            })
                        else:
                            pass
                    except Exception as e:
                        self.messagem.setText(f"Erro ao salvar dados no Firestore: {e}")
                        self.messagem.setStyleSheet("font-weight: bold; color: red;")
                        return
                    QMessageBox.information(self, "Sucesso", f"Romaneio salvo com sucesso.")
                    self.messagem.setText(f"Insira o proximo entregador e realize as bipagems!")
                    self.messagem.setStyleSheet("font-weight: bold; color: blue;")
                    
                    self.ResetList()
                else:
                    self.messagem.setText(f"Prossiga com a bipagem normalmente.")
                    self.messagem.setStyleSheet("font-weight: bold; color: blue;")
            
            else:
                self.messagem.setText("Por favor, defina nome e entregador \nantes de exportar.")
                self.messagem.setStyleSheet("font-weight: bold; color: red;")
        except Exception as e:
            self.messagem.setText(f"Erro inesperado: {e}")
            self.messagem.setStyleSheet("font-weight: bold; color: red;")
  
    def ResetList(self):
        self.insertedBarCodes.clear()
        if not self.cidade_label.text() == "Local:":
            self.entregador_input.clear()
        if os.path.exists("insertedBarCodes.txt"): os.remove("insertedBarCodes.txt")
        self.UpdateBarCodeListWidget()

    def DeleteBarCode(self):
        selected_items = self.codigos_list_widget.selectedItems()
        if not selected_items: return
        for item in selected_items:
            codigo = item.text()
            self.insertedBarCodes.remove(codigo)
            self.codigos_list_widget.takeItem(self.codigos_list_widget.row(item))
            self.counter -= 1
            self.counter_label.setText(f"Quantidade: {self.counter}")
        self.salvar_insertedBarCodes()
        self.search_input.clear()

    def salvar_insertedBarCodes(self):
        with open("insertedBarCodes.txt", "w") as file:
            for codigo in self.insertedBarCodes:
                file.write(f"{codigo}\n")

    def FilterBarCodes(self):
        search_term = self.search_input.text().lower()
        self.codigos_list_widget.clear()
        for codigo in self.insertedBarCodes:
            if search_term in codigo.lower(): self.codigos_list_widget.addItem(codigo)

    def AddBarCode(self):
        barCode = self.AddBarCode_input.text()
        if barCode in self.insertedBarCodes:
            self.AddBarCode_input.clear()
            self.bring_to_front()
            winsound.Beep(820, 1000)
            self.messagem.setText("Código de barras já inserido.")
            self.messagem.setStyleSheet("font-weight: bold; color: red;")
            return
        if barCode:
            self.insertedBarCodes.add(barCode)
            self.SaveBarCode(barCode)
            self.UpdateBarCodeListWidget()
            self.sound_success()
            self.AddBarCode_input.clear()
        else: 
            self.messagem.setText("Insira um código válido.")
            self.messagem.setStyleSheet("font-weight: bold; color: red;")

def InsertBarCode(barCode, x, y, x2, y2, tempo1, tempo2, tempTwo, tempOne):
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