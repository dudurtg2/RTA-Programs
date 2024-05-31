import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox, QListWidget, QFileDialog
import pyautogui
import pyperclip
import time
import pygetwindow as gw
import winsound
import keyboard
import os

class MouseCoordinateApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bipagem unica - C.E.O.S")

        layout = QVBoxLayout()

        self.label = QLabel("Clique nos botões para definir a posição do mouse:                    ")
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

        self.entry_label = QLabel("Insira o código de barras:")
        layout.addWidget(self.entry_label)
        self.entry = QLineEdit()
        layout.addWidget(self.entry)

        self.counter_label = QLabel("Contador: 0")
        layout.addWidget(self.counter_label)

        self.reset_button = QPushButton("Resetar Contador")
        self.reset_button.clicked.connect(self.reset_counter)
        layout.addWidget(self.reset_button)

        tempo_layout = QHBoxLayout()
        self.label_tempo1 = QLabel("Tempo de colagem (s):")
        tempo_layout.addWidget(self.label_tempo1)
        self.tempo1_spinbox = QSpinBox()
        self.tempo1_spinbox.setRange(100, 5000)  # Valores em milissegundos
        tempo_layout.addWidget(self.tempo1_spinbox)
        layout.addLayout(tempo_layout)

        tempo_layout = QHBoxLayout()
        self.label_tempo2 = QLabel("Tempo de press enter:")
        tempo_layout.addWidget(self.label_tempo2)
        self.tempo2_spinbox = QSpinBox()
        self.tempo2_spinbox.setRange(100, 5000)  # Valores em milissegundos
        tempo_layout.addWidget(self.tempo2_spinbox)
        layout.addLayout(tempo_layout)

        tempo_layout = QHBoxLayout()
        self.label_tempo3 = QLabel("Tempo do mouse:")
        tempo_layout.addWidget(self.label_tempo3)
        self.tempo3_spinbox = QSpinBox()
        self.tempo3_spinbox.setRange(500, 5000)  # Valores em milissegundos
        tempo_layout.addWidget(self.tempo3_spinbox)
        layout.addLayout(tempo_layout)

        self.codigos_list_widget = QListWidget()
        layout.addWidget(self.codigos_list_widget)

        self.export_button = QPushButton("Exportar Lista")
        self.export_button.clicked.connect(self.exportar_lista)
        layout.addWidget(self.export_button)

        self.reset_list_button = QPushButton("Resetar Lista")
        self.reset_list_button.clicked.connect(self.resetar_lista)
        layout.addWidget(self.reset_list_button)

        self.setLayout(layout)

        self.positions = {}
        self.counter = 0

        self.entry.returnPressed.connect(self.start_inserir_codigo)

        self.codigos_inseridos = self.carregar_codigos_inseridos()
        self.update_codigos_list_widget()

    def set_position1(self):
        print("Posicione o mouse e pressione Enter.")
        keyboard.wait("enter")
        x, y = pyautogui.position()
        self.positions['pos1'] = (x, y)
        self.coord_label1.setText(f"Posição 1: ({x}, {y})")

    def set_position2(self):
        print("Posicione o mouse e pressione Enter.")
        keyboard.wait("enter")
        x, y = pyautogui.position()
        self.positions['pos2'] = (x, y)
        self.coord_label2.setText(f"Posição 2: ({x}, {y})")

    def carregar_codigos_inseridos(self):
        if os.path.exists("codigos_inseridos.txt"):
            with open("codigos_inseridos.txt", "r") as file:
                return set(file.read().splitlines())
        return set()

    def salvar_codigo(self, codigo):
        with open("codigos_inseridos.txt", "a") as file:
            file.write(f"{codigo}\n")

    def update_codigos_list_widget(self):
        self.codigos_list_widget.clear()
        self.codigos_list_widget.addItems(self.codigos_inseridos)

    def start_inserir_codigo(self):
        if 'pos1' in self.positions and 'pos2' in self.positions:
            codigo_barras = self.entry.text()
            if len(codigo_barras) < 1:
                print("Código de barras inválido. Insira um código com pelo menos 1 caractere.")
                return

            if codigo_barras in self.codigos_inseridos:
                self.entry.clear()
                self.bring_to_front()
                winsound.Beep(820, 1000)
                print("Código de barras já inserido.")
                return

            self.codigos_inseridos.add(codigo_barras)
            self.salvar_codigo(codigo_barras)

            tempo1 = self.tempo1_spinbox.value() / 1000 
            tempo2 = self.tempo2_spinbox.value() / 1000 
            tempo3 = self.tempo3_spinbox.value() / 1000 

            inserir_codigo(codigo_barras, *self.positions['pos1'], *self.positions['pos2'], tempo1, tempo2, tempo3)
            self.entry.clear()  

            self.counter += 1
            self.counter_label.setText(f"Contador: {self.counter}")

            self.bring_to_front()

            winsound.Beep(3520, 250)
            self.update_codigos_list_widget()
        else:
            print("Por favor, defina todas as posições antes de iniciar.")

    def bring_to_front(self):
        window = gw.getWindowsWithTitle(self.windowTitle())[0]
        if window:
            window.activate()

    def reset_counter(self):
        self.counter = 0
        self.counter_label.setText(f"Contador: {self.counter}")

    def exportar_lista(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Lista", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, "w") as file:
                for codigo in self.codigos_inseridos:
                    file.write(f"{codigo}\n")

    def resetar_lista(self):
        self.codigos_inseridos.clear()
        if os.path.exists("codigos_inseridos.txt"):
            os.remove("codigos_inseridos.txt")
        self.update_codigos_list_widget()

def inserir_codigo(codigo_barras, x, y, x2, y2, tempo1, tempo2, tempo3):
    coordenadas_abas = {
        'aba1': {'campo1': (x, y), 'campo2': (x, y)},
        'aba2': {'campo1': (x2, y2), 'campo2': (x2, y2)}
    }

    pyperclip.copy(codigo_barras)

    for aba, campos in coordenadas_abas.items():
        for campo, coordenadas in campos.items():
            pyautogui.moveTo(*coordenadas, duration=tempo3)
            pyautogui.click()
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(tempo1)
            pyautogui.press('enter')
            time.sleep(tempo2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MouseCoordinateApp()
    widget.show()
    sys.exit(app.exec_())
