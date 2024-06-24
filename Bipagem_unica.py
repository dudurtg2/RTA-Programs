import datetime
import sys
import json
import pyautogui
import pyperclip
import time
import winsound
import keyboard
import os
import qrcode
import io
import pymysql
import subprocess

import pygetwindow as gw

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
    QComboBox
)
from PyQt5.QtPrintSupport import (
    QPrinter,
    QPrintDialog
)

cidades = [
    "IPIRA", "BAIXA GRANDE", "MAIRI", "VARZEA DA ROÇA", "MORRO DO CHAPEU", "IRECE",
    "ITABERABA", "IAÇU", "ITATIM", "CASTRO ALVES", "SANTA TEREZINHA", "SANTO ESTEVÃO",
    "ANTONIO CARDOSO", "IPECAETA", "SÃO GONÇALO DOS CAMPOS", "CACHOEIRA", "SÃO FELIX",
    "CONCEIÇÃO DA FEIRA", "AMELIA RODRIGUES", "CONCEIÇÃO DO JACUIPE", "CORAÇÃO DE MARIA",
    "TEODORO SAMPAIO", "IRARA", "SANTANOPOLIS", "MURITIBA", "SAPEAÇU", "CRUZ DAS ALMAS",
    "GOVERNADOR MANGABEIRA", "CABACEIRA DO PARAGUAÇU", "CONCEIÇÃO DO ALMEIDA", "SÃO FELIPE",
    "MARAGOGIPE", "TANQUINHO", "CANDEAL", "ICHU", "SERRINHA", "BIRITINGA", "BARROCAS",
    "ARACI", "TEOFILANDIA", "SANTA BARBARA", "LAMARÃO", "AGUA FRIA", "CONCEIÇÃO DO COITÉ",
    "VALENTE", "RETIROLANDIA", "SANTA LUZ", "CANSANÇÃO", "QUEIMADAS", "SÃO DOMINGOS",
    "RIACHÃO DO JACUIPE", "NOVA FATIMA", "PE DE SERRA", "CIPÓ", "BANZAÊ", "FATIMA",
    "CICERO DANTAS", "NOVA SOURE", "TUCANO", "RIBEIRA DO AMPARO", "SITIO DO QUINTO",
    "CORONEL JOÃO SÁ", "HELIOPOLIS", "RIBEIRA DO POMBAL", "ANGUERA", "SERRA PRETA",
    "RAFAEL JAMBEIRO", "ALAGOINHAS", "JACOBINA", "SANTO ANTONIO DE JESUS", 
    "FEIRA DE SANTANA", "CIDADES DE ALAGOINHAS", "CIDADES DE SANTO ANTONIO DE JESUS",
    "CIDADES DE JACOBINA", "DEVOLUÇÃO"
]
cidades_ordenadas = sorted(cidades)
class MouseCoordinateApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de bipagem unica")

        layout = QVBoxLayout()

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
        
        self.layout_cidade = QHBoxLayout()
        self.cidade_label = QLabel("Cidade:")
        self.layout_cidade.addWidget(self.cidade_label)
        self.combo_box = QComboBox()
        self.combo_box.addItems(cidades_ordenadas)
        self.layout_cidade.addWidget(self.combo_box)
        layout.addLayout(self.layout_cidade)

        self.label = QLabel("Clique nos botões para definir a posição do mouse:")
        self.label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.label)

        position_layout = QHBoxLayout()
        self.coord_label1 = QLabel("Posição 1: Não definida")
        position_layout.addWidget(self.coord_label1)
        self.button1 = QPushButton("Definir Posição 1")
        self.button1.clicked.connect(self.set_position1)
        position_layout.addWidget(self.button1)
        layout.addLayout(position_layout)

        position_layout = QHBoxLayout()
        self.coord_label2 = QLabel("Posição 2: Não definida")
        position_layout.addWidget(self.coord_label2)
        self.button2 = QPushButton("Definir Posição 2")
        self.button2.clicked.connect(self.set_position2)
        position_layout.addWidget(self.button2)
        layout.addLayout(position_layout)

        tempo_layout = QHBoxLayout()
        layout.addLayout(tempo_layout)

        self.label_tempo1 = QLabel("Tempo de colagem:")
        tempo_layout.addWidget(self.label_tempo1)
        self.tempo1_spinbox = QSpinBox()
        self.tempo1_spinbox.setRange(0, 5000)
        tempo_layout.addWidget(self.tempo1_spinbox)

        self.label_tempo2 = QLabel("Tempo de espera:")
        tempo_layout.addWidget(self.label_tempo2)
        self.tempo2_spinbox = QSpinBox()
        self.tempo2_spinbox.setRange(0, 5000)
        tempo_layout.addWidget(self.tempo2_spinbox)

        tempo_layout_base = QHBoxLayout()
        layout.addLayout(tempo_layout_base)

        self.label_tempo_base = QLabel("Bipagem na base:")
        tempo_layout_base.addWidget(self.label_tempo_base)
        self.tempo_base_spinbox = QSpinBox()
        self.tempo_base_spinbox.setRange(0, 5)
        tempo_layout_base.addWidget(self.tempo_base_spinbox)

        self.label_tempo_entregador = QLabel("Bipagem no entregador:")
        tempo_layout_base.addWidget(self.label_tempo_entregador)
        self.tempo_entregador_spinbox = QSpinBox()
        self.tempo_entregador_spinbox.setRange(0, 5)
        tempo_layout_base.addWidget(self.tempo_entregador_spinbox)

        self.label = QLabel("Clique no campo abaixo para inserir os códigos:")
        self.label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.label)

        self.entry = QLineEdit()
        layout.addWidget(self.entry)

        self.counter_label = QLabel("Contador: 0")
        self.counter_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.counter_label)

        self.layout_search_label = QHBoxLayout()
        self.search_label = QLabel("Busca na lista:")
        self.layout_search_label.addWidget(self.search_label)
        self.search_input = QLineEdit()
        self.layout_search_label.addWidget(self.search_input)
        self.search_input.textChanged.connect(self.filtrar_codigos)
        layout.addLayout(self.layout_search_label)

        self.delete_button = QPushButton("Delete o codigo selecionado")
        self.delete_button.setStyleSheet("color: red;")
        self.delete_button.clicked.connect(self.deletar_codigo)
        layout.addWidget(self.delete_button)

        self.codigos_list_widget = QListWidget()
        layout.addWidget(self.codigos_list_widget)

        self.adicionar_codigos = QLabel("Insira manualmente o código de barras:")
        layout.addWidget(self.adicionar_codigos)
        self.adicionar_codigo_input = QLineEdit()
        layout.addWidget(self.adicionar_codigo_input)

        self.button = QHBoxLayout()
        self.export_button = QPushButton("Exportar Lista")
        self.button.addWidget(self.export_button)
        self.export_button.clicked.connect(self.exportar_lista)

        self.reset_list_button = QPushButton("Resetar Lista")
        self.button.addWidget(self.reset_list_button)
        self.reset_list_button.clicked.connect(self.resetar_lista)

        layout.addLayout(self.button)

        self.messagem = QLabel("Defina as posicoes dos mouse e aperte Enter.")
        layout.addWidget(self.messagem)
        
        sound_layout = QHBoxLayout()
        layout.addLayout(sound_layout)
        
        self.sound_text = QLabel("Perfil de som:")
        sound_layout.addWidget(self.sound_text)
        self.sound_imput = QSpinBox()
        self.sound_imput.setRange(0, 8000)
        sound_layout.addWidget(self.sound_imput)

        self.ceos_label_layout = QHBoxLayout()
        self.Ceos = QLabel("C.E.O.S - 0.11.2Beta LC-transporte")
        self.Ceos.setStyleSheet("color: gray;")
        self.ceos_label_layout.addWidget(self.Ceos)
        self.ceos_label_layout.setAlignment(Qt.AlignRight)
        layout.addLayout(self.ceos_label_layout)

        self.setLayout(layout)
        self.tempo_entregador_spinbox.setValue(1)
        self.tempo_base_spinbox.setValue(2)
        self.tempo2_spinbox.setValue(800)
        self.tempo1_spinbox.setValue(150)
        self.sound_imput.setValue(3520)
        self.positions = {}
        self.counter = 0
        self.adicionar_codigo_input.returnPressed.connect(self.adicionar_codigo)
        self.entry.returnPressed.connect(self.start_inserir_codigo)
        self.codigos_inseridos = self.carregar_codigos_inseridos()
        self.update_codigos_list_widget()
        
    def on_cidade_selected(self, index):
        selected_cidade = self.combo_box.currentText()
        self.selected_label.setText(f"Cidade selecionada: {selected_cidade}")
        
    def set_position1(self):
        self.messagem.setText("Posicione o mouse e pressione Enter.")
        keyboard.wait("enter")
        x, y = pyautogui.position()
        self.positions["pos1"] = (x, y)
        self.coord_label1.setText(f"Posição 1: ({x}, {y})")

    def set_position2(self):
        self.messagem.setText("Posicione o mouse e pressione Enter.")
        keyboard.wait("enter")
        x, y = pyautogui.position()
        self.positions["pos2"] = (x, y)
        self.coord_label2.setText(f"Posição 2: ({x}, {y})")

    def carregar_codigos_inseridos(self):
        codigos_inseridos = set()
        if os.path.exists("codigos_inseridos.txt"):
            with open("codigos_inseridos.txt", "r") as file:
                for linha in file:
                    linha = linha.strip()
                    if linha: codigos_inseridos.add(linha)
        return codigos_inseridos

    def salvar_codigo(self, codigo):
        with open("codigos_inseridos.txt", "a") as file:
            if not file.tell(): file.write("\n")
            file.write(f"{codigo}\n")

    def update_codigos_list_widget(self):
        self.codigos_list_widget.clear()
        self.codigos_list_widget.addItems(self.codigos_inseridos)
        if self.codigos_inseridos: self.counter = len(self.codigos_inseridos)
        else: self.counter = 0
        self.counter_label.setText(f"Contador: {self.counter}")

    def sound_success(self): winsound.Beep(int(self.sound_imput.value()) , 250)
        
    def start_inserir_codigo(self):
        if ( "pos1" in self.positions and "pos2" in self.positions and self.nome_input.text() != "" and self.entregador_input.text() != "" ):
            codigo_barras = self.entry.text()
            if len(codigo_barras) < 1:
                self.messagem.setText( "Código de barras inválido. \nInsira um código com pelo menos 1 caractere." )
                return
            
            if codigo_barras in self.codigos_inseridos:
                self.entry.clear()
                self.bring_to_front()
                winsound.Beep(820, 1000)
                self.messagem.setText("Código de barras já inserido.")
                return

            self.codigos_inseridos.add(codigo_barras)
            self.salvar_codigo(codigo_barras)
            
            inserir_codigo(codigo_barras, *self.positions["pos1"], *self.positions["pos2"], self.tempo1_spinbox.value() / 1000, self.tempo2_spinbox.value() / 1000, self.tempo_entregador_spinbox.value(), self.tempo_base_spinbox.value())
            
            self.entry.clear()
            self.sound_success()
            self.bring_to_front()
            self.update_codigos_list_widget() 
        else: self.messagem.setText( "Por favor, defina todas as posições, nome e entregador\nantes de iniciar." )
            
    def bring_to_front(self):
        window = gw.getWindowsWithTitle(self.windowTitle())[0]
        if window: window.activate()
            
    def exportar_lista(self):
        if ("pos1" in self.positions and "pos2" in self.positions and self.nome_input.text() != "" and self.entregador_input.text() != ""):
            options = QFileDialog.Options()
            now = datetime.datetime.now()
            formatted_code = now.strftime("RTA%Y%m%d%H%M%S%f")[:-3] + "LC"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar Lista",
                formatted_code + ", cidade. " + self.combo_box.currentText(),
                "PDF Files (*.pdf);;All Files (*)",
                options=options,
            )
            
            if file_path:
                c = canvas.Canvas(file_path, pagesize=letter)
                now = datetime.datetime.now()
                formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
                folder_date = now.strftime("%d-%m-%Y")
                folder_name = self.entregador_input.text().upper()
                folder_first = self.nome_input.text().upper()
                
                c.drawString(70, 750, "Hora e Dia: " + formatted_now)
                c.drawString(70, 735, "Funcionario: " + self.nome_input.text())
                c.drawString(70, 720, "Entregador: " + self.entregador_input.text())
                c.drawString(70, 705, self.counter_label.text())
                c.drawString(70, 690, "Cidade: " + self.combo_box.currentText())
                c.drawString(70, 675, "Codigo de ficha: " + formatted_code)
                c.drawString(70, 655, "Codigos inseridos:")
                
                y = 635
                for codigo in self.codigos_inseridos:
                    if y < 50:
                        c.showPage()
                        y = 750
                    c.drawString(70, y, str(codigo))
                    y -= 12
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
                
                c.drawImage(ImageReader(qr_buffer), 400, 665, 100, 100) 
                c.save()
                    
                credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/drive"])
                drive_service = build("drive", "v3", credentials=credentials)
    
                def find_or_create_folder(folder_name, parent_id=None):
                    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                    if parent_id: query += f" and '{parent_id}' in parents"
                    response = drive_service.files().list(
                        q=query,
                        spaces="drive",
                        fields="files(id, name)",
                    ).execute()
                    files = response.get("files", [])
                    if files: return files[0]["id"]
                    else:
                        folder_metadata = {
                            "name": folder_name,
                            "mimeType": "application/vnd.google-apps.folder",
                        }
                        if parent_id: folder_metadata["parents"] = [parent_id]
                        folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
                        return folder["id"]
                    
                main_folder_id = find_or_create_folder(folder_date, "15K7K7onfz98E2UV31sFHWIQf7RGWhApV")
                first_subfolder_id = find_or_create_folder(folder_first, main_folder_id)
                second_subfolder_id = find_or_create_folder(folder_name, first_subfolder_id)
    
                file_metadata = {
                    "name": os.path.basename(file_path),
                    "mimeType": "application/pdf",
                    "parents": [second_subfolder_id],
                }
                media = MediaFileUpload(file_path, mimetype="application/pdf")
                drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
                
                self.resetar_lista()
        else: self.messagem.setText("Por favor, defina todas as posições, nome e entregador\nantes de exportar.")
    
    def resetar_lista(self):
        self.codigos_inseridos.clear()
        if os.path.exists("codigos_inseridos.txt"): os.remove("codigos_inseridos.txt")
        self.update_codigos_list_widget()

    def deletar_codigo(self):
        selected_items = self.codigos_list_widget.selectedItems()
        if not selected_items: return
        for item in selected_items:
            codigo = item.text()
            self.codigos_inseridos.remove(codigo)
            self.codigos_list_widget.takeItem(self.codigos_list_widget.row(item))
            self.counter -= 1
            self.counter_label.setText(f"Contador: {self.counter}")
        self.salvar_codigos_inseridos()
        self.search_input.clear()

    def salvar_codigos_inseridos(self):
        with open("codigos_inseridos.txt", "w") as file:
            for codigo in self.codigos_inseridos:
                file.write(f"{codigo}\n")

    def filtrar_codigos(self):
        search_term = self.search_input.text().lower()
        self.codigos_list_widget.clear()
        for codigo in self.codigos_inseridos:
            if search_term in codigo.lower(): self.codigos_list_widget.addItem(codigo)

    def adicionar_codigo(self):
        codigo_barras = self.adicionar_codigo_input.text()
        if codigo_barras in self.codigos_inseridos:
            self.adicionar_codigo_input.clear()
            self.bring_to_front()
            winsound.Beep(820, 1000)
            self.messagem.setText("Código de barras já inserido.")
            return
        if codigo_barras:
            self.codigos_inseridos.add(codigo_barras)
            self.salvar_codigo(codigo_barras)
            self.update_codigos_list_widget()
            self.adicionar_codigo_input.clear()
        else: self.messagem.setText("Insira um código válido.")

def inserir_codigo(codigo_barras, x, y, x2, y2, tempo1, tempo2, tempo_entregador, tempo_base):
    coordenadas_base = [(x, y)] * tempo_base
    coordenadas_entregador = [(x2, y2)] * tempo_entregador
    coordenadas_abas = {
        "aba1": {f"campo{i+1}": coord for i, coord in enumerate(coordenadas_base)},
        "aba2": {f"campo{i+1}": coord for i, coord in enumerate(coordenadas_entregador)},
    }
    pyperclip.copy(codigo_barras)
    for aba, campos in coordenadas_abas.items():
        for campo, coordenadas in campos.items():
            pyautogui.moveTo(*coordenadas, duration=0)
            pyautogui.click()
            pyautogui.hotkey("ctrl", "v")
            time.sleep(tempo1)
            pyautogui.press("enter")
            time.sleep(tempo1)
        time.sleep(tempo2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MouseCoordinateApp()
    widget.show()
    sys.exit(app.exec_())
