import tkinter as tk
import pyautogui
import pyperclip
import time
import pygetwindow as gw
import winsound
import keyboard

class MouseCoordinateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bipagem unica - C.E.O.S")
        
        self.label = tk.Label(root, text="Clique nos botões para definir a posição do mouse:       ")
        self.label.pack(pady=10)

        self.coord_label1 = tk.Label(root, text="Posição 1: Não definida")
        self.coord_label1.pack(pady=5)
        
        self.coord_label2 = tk.Label(root, text="Posição 2: Não definida")
        self.coord_label2.pack(pady=5)

        self.button1 = tk.Button(root, text="Definir Posição 1", command=self.set_position1)
        self.button1.pack(pady=5)

        self.button2 = tk.Button(root, text="Definir Posição 2", command=self.set_position2)
        self.button2.pack(pady=5)

        self.entry_label = tk.Label(root, text="Insira o código de barras:")
        self.entry_label.pack(pady=10)

        self.entry = tk.Entry(root)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>', self.start_inserir_codigo)

        self.counter_label = tk.Label(root, text="Contador: 0")
        self.counter_label.pack(pady=10)

        self.reset_button = tk.Button(root, text="Resetar Contador", command=self.reset_counter)
        self.reset_button.pack(pady=5)

        self.positions = {}
        self.counter = 0

    def set_position(self, position_key):
        print("Posicione o mouse e pressione Enter.")
        keyboard.wait("enter")
        x, y = pyautogui.position()
        self.positions[position_key] = (x, y)
        print(f"Coordenadas definidas para {position_key}: ({x}, {y})")

        if position_key == 'pos1':
            self.coord_label1.config(text=f"Posição 1: ({x}, {y})")
        elif position_key == 'pos2':
            self.coord_label2.config(text=f"Posição 2: ({x}, {y})")

    def set_position1(self):
        self.set_position('pos1')

    def set_position2(self):
        self.set_position('pos2')

    def start_inserir_codigo(self, event=None):
        if 'pos1' in self.positions and 'pos2' in self.positions:
            codigo_barras = self.entry.get()
            if len(codigo_barras) < 1:
                print("Código de barras inválido. Insira um código com pelo menos 1 caractere.")
                return

            inserir_codigo(codigo_barras, *self.positions['pos1'], *self.positions['pos2'])
            self.entry.delete(0, tk.END) 

            
            self.counter += 1
            self.counter_label.config(text=f"Contador: {self.counter}")

            
            self.bring_to_front()

            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            print("Por favor, defina todas as posições antes de iniciar.")

    def bring_to_front(self):
        window = gw.getWindowsWithTitle(self.root.title())[0]
        if window:
            window.activate()

    def reset_counter(self):
        self.counter = 0
        self.counter_label.config(text=f"Contador: {self.counter}")

def inserir_codigo(codigo_barras, x, y, x2, y2):
    coordenadas_abas = {
        'aba1': {'campo1': (x, y), 'campo2': (x, y)},
        'aba2': {'campo1': (x2, y2), 'campo2': (x2, y2)}
    }

    pyperclip.copy(codigo_barras) 

    for aba, campos in coordenadas_abas.items():
        for i, (campo, coordenadas) in enumerate(campos.items()):
            pyautogui.moveTo(*coordenadas, duration=0)
            pyautogui.click()
            
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            pyautogui.press('enter')
            time.sleep(0.1)
            if i == 0: 
                time.sleep(0.7)

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseCoordinateApp(root)
    root.mainloop()
