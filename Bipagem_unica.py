import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox
import pyautogui
import pyperclip
import time
import pygetwindow as gw
import winsound
import keyboard

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
        self.tempo1_spinbox.setRange(100, 5000)  
        tempo_layout.addWidget(self.tempo1_spinbox)
        layout.addLayout(tempo_layout)

        tempo_layout = QHBoxLayout()
        self.label_tempo2 = QLabel("Tempo de press enter:")
        tempo_layout.addWidget(self.label_tempo2)
        self.tempo2_spinbox = QSpinBox()
        self.tempo2_spinbox.setRange(100, 5000) 
        tempo_layout.addWidget(self.tempo2_spinbox)
        layout.addLayout(tempo_layout)

        tempo_layout = QHBoxLayout()
        self.label_tempo3 = QLabel("Tempo do mouse:")
        tempo_layout.addWidget(self.label_tempo3)
        self.tempo3_spinbox = QSpinBox()
        self.tempo3_spinbox.setRange(250, 5000)  
        tempo_layout.addWidget(self.tempo3_spinbox)
        layout.addLayout(tempo_layout)

        self.setLayout(layout)

        self.positions = {}
        self.counter = 0
        self.entry.returnPressed.connect(self.start_inserir_codigo)
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

    def start_inserir_codigo(self):
        if 'pos1' in self.positions and 'pos2' in self.positions:
            codigo_barras = self.entry.text()
            if len(codigo_barras) < 1:
                print("Código de barras inválido. Insira um código com pelo menos 1 caractere.")
                return

            tempo1 = self.tempo1_spinbox.value() / 1000 
            tempo2 = self.tempo2_spinbox.value() / 1000 
            tempo3 = self.tempo3_spinbox.value() / 1000 

            inserir_codigo(codigo_barras, *self.positions['pos1'], *self.positions['pos2'], tempo1, tempo2, tempo3)
            self.entry.clear() 

            self.counter += 1
            self.counter_label.setText(f"Contador: {self.counter}")

            self.bring_to_front()

            winsound.Beep(3520, 250)
        else:
            print("Por favor, defina todas as posições antes de iniciar.")

    def bring_to_front(self):
        window = gw.getWindowsWithTitle(self.windowTitle())[0]
        if window:
            window.activate()

    def reset_counter(self):
        self.counter = 0
        self.counter_label.setText(f"Contador: {self.counter}")

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
