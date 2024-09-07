import pyautogui
import pyperclip
import time

# Array com 3 palavras
palavras = [""]

# Função para colar as palavras na posição atual do mouse
def colar_palavras(palavras):
    for palavra in palavras:
        pyperclip.copy(palavra)  # Copia a palavra para a área de transferência
        pyautogui.hotkey('ctrl', 'v')  # Cola o conteúdo da área de transferência
        pyautogui.press('enter')       # Pressiona 'Enter' para ir para a próxima linha
        time.sleep(1)  # Espera meio segundo entre cada palavra

# Espera alguns segundos antes de iniciar para você posicionar o cursor do mouse
print("Posicione o cursor do mouse onde deseja colar as palavras. Iniciando em 5 segundos...")
time.sleep(3)

# Chama a função para colar as palavras
colar_palavras(palavras)