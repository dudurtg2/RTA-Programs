import tkinter as tk
import pyautogui
import time

class ClickApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clique nos Pontos")

        self.point_vars = [tk.StringVar() for _ in range(6)]
        self.entries = []

        self.create_widgets()
        self.current_point = 0

    def create_widgets(self):
        for i in range(3):
            tk.Label(self.root, text=f"Ponto {i+1} (x, y):").grid(row=i, column=0, padx=10, pady=10)
            entry_x = tk.Entry(self.root, textvariable=self.point_vars[i*2])
            entry_x.grid(row=i, column=1, padx=10, pady=10)
            entry_y = tk.Entry(self.root, textvariable=self.point_vars[i*2+1])
            entry_y.grid(row=i, column=2, padx=10, pady=10)
            self.entries.append((entry_x, entry_y))

        self.set_button = tk.Button(self.root, text="Definir Ponto", command=self.set_point)
        self.set_button.grid(row=3, column=0, columnspan=3, pady=10)

        self.click_button = tk.Button(self.root, text="Clicar nos Pontos", command=self.click_points)
        self.click_button.grid(row=4, column=0, columnspan=3, pady=10)

        self.status_label = tk.Label(self.root, text="")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=10)

        self.root.bind('<Return>', self.enter_pressed)

    def set_point(self):
        if self.current_point < 3:
            self.status_label.config(text=f"Movimente o mouse para o Ponto {self.current_point + 1} e pressione Enter")
        else:
            self.status_label.config(text="Todos os pontos já foram definidos")

    def enter_pressed(self, event):
        if self.current_point < 3:
            x, y = pyautogui.position()
            self.point_vars[self.current_point * 2].set(x)
            self.point_vars[self.current_point * 2 + 1].set(y)
            self.current_point += 1
            self.status_label.config(text=f"Ponto {self.current_point} definido: ({x}, {y})")
            if self.current_point < 3:
                self.status_label.config(text=f"Movimente o mouse para o Ponto {self.current_point + 1} e pressione Enter")

    def click_points(self):
        try:
            points = [(int(self.point_vars[i].get()), int(self.point_vars[i + 1].get())) for i in range(0, 6, 2)]
            wait_time = 1 
            
            time.sleep(5)

            for point in points:
                pyautogui.moveTo(point[0], point[1])
                pyautogui.click()
                time.sleep(wait_time)

            self.status_label.config(text="Clicou nos três pontos com sucesso!")
        except ValueError:
            self.status_label.config(text="Por favor, defina todos os pontos corretamente.")

root = tk.Tk()
app = ClickApp(root)

root.mainloop()
