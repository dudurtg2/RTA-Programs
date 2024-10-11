import sys
import pyautogui
import pyperclip
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QTextEdit, QLabel, QSpinBox, QHBoxLayout, QProgressBar, QMessageBox)
from PyQt5.QtCore import QTimer

class ColarPalavrasApp(QWidget):
    def __init__(self):
        super().__init__()

        # Variável para controlar se a colagem está em andamento
        self.colagem_ativa = False
        self.timer = QTimer()

        self.initUI()

    def initUI(self):
        # Layout principal
        layout = QVBoxLayout()

        # Label de instrução
        self.label = QLabel("Insira as palavras (uma por linha) para colar na posição atual do mouse:")
        layout.addWidget(self.label)

        # Campo de texto para inserir palavras
        self.textEdit = QTextEdit(self)
        layout.addWidget(self.textEdit)

        # Campo para inserir o tempo entre colagens
        tempo_layout = QHBoxLayout()
        self.tempo_label = QLabel("Tempo entre colagens (segundos):")
        self.tempo_spinbox = QSpinBox(self)
        self.tempo_spinbox.setRange(1, 10)  # Define intervalo de 1 a 10 segundos
        self.tempo_spinbox.setValue(2)  # Define o valor padrão como 2 segundos

        tempo_layout.addWidget(self.tempo_label)
        tempo_layout.addWidget(self.tempo_spinbox)
        layout.addLayout(tempo_layout)

        # Barra de progresso para mostrar o progresso de colagem
        self.progressBar = QProgressBar(self)
        layout.addWidget(self.progressBar)

        # Layout para os botões lado a lado
        button_layout = QHBoxLayout()

        # Botão para iniciar a colagem
        self.button_colar = QPushButton('Colar Palavras', self)
        self.button_colar.clicked.connect(self.iniciar_contagem)
        button_layout.addWidget(self.button_colar)

        # Botão para apagar tudo
        self.button_limpar = QPushButton('Apagar Tudo', self)
        self.button_limpar.clicked.connect(self.limpar_texto)
        button_layout.addWidget(self.button_limpar)

        # Botão para parar a colagem
        self.button_parar = QPushButton('Parar Colagem', self)
        self.button_parar.clicked.connect(self.parar_colagem)
        button_layout.addWidget(self.button_parar)

        layout.addLayout(button_layout)

        # Configuração da janela
        self.setLayout(layout)
        self.setWindowTitle('Colar Palavras')
        self.setGeometry(300, 300, 400, 300)

    def iniciar_contagem(self):
        self.progressBar.setValue(0)
        self.timer.timeout.connect(self.atualizar_progressao)
        self.contador = 5  # 5 segundos para o posicionamento do mouse
        self.colagem_ativa = True  # Marca que a colagem está ativa
        self.timer.start(1000)  # Atualiza a cada 1 segundo

    def atualizar_progressao(self):
        if self.contador > 0:
            self.contador -= 1
        else:
            self.timer.stop()
            self.colar_palavras()

    def colar_palavras(self):
        palavras = self.textEdit.toPlainText().splitlines()
        total_palavras = len(palavras)
        tempo_entre_colagens = self.tempo_spinbox.value()

        # Configura a barra de progresso para o total de palavras
        self.progressBar.setRange(0, total_palavras)
        self.progressBar.setValue(0)

        for index, palavra in enumerate(palavras):
            if not self.colagem_ativa:  # Verifica se a colagem foi interrompida
                return

            if palavra.strip():  # Evita linhas vazias
                pyperclip.copy(palavra)
                pyautogui.hotkey('ctrl', 'v')
                pyautogui.press('enter')
                time.sleep(tempo_entre_colagens)

            # Atualiza a barra de progresso com base na quantidade de palavras já coladas
            self.progressBar.setValue(index + 1)

        self.exibir_mensagem("Colagem finalizada!", "A colagem das palavras foi concluída.")

    def limpar_texto(self):
        self.textEdit.clear()

    def parar_colagem(self):
        self.colagem_ativa = False  # Define que a colagem deve ser interrompida

    def exibir_mensagem(self, titulo, mensagem):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(titulo)
        msg.setText(mensagem)
        msg.exec_()

# Função principal para rodar o app
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ColarPalavrasApp()
    ex.show()
    sys.exit(app.exec_())
