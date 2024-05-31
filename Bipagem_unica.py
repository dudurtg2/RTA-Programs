import pyautogui
import keyboard
import time
import os

def mostrar_coordenadas():
    print("O programa irá mostrar as coordenadas do mouse após 2 segundos.")
    time.sleep(2) 

    x, y = pyautogui.position()
    positionStr = f'{x},{y}'
    print(positionStr)
    keyboard.wait("enter") 

    return x, y

def inserir_codigo(x, y, x2, y2, x3, y3):
    coordenadas_abas = {
        'aba1': {'campo1': (x, y), 'campo2': (x, y)},
        'aba2': {'campo1': (x2, y2), 'campo2': (x2, y2)},
        'aba3': {'campo1': (x3, y3)}
    }

    while True:
        os.system('cls')
        codigo_barras = input("SO REALIZAR A BIPAGEM APOS ESSA MENSAGEM: ")
        
        if codigo_barras.lower() == 'sair':
            print("Saindo do programa.")
            break

        if len(codigo_barras) < 1:
            print("Código de barras inválido. Insira um código com pelo menos 1 caractere.")
            continue

        for aba, campos in coordenadas_abas.items():
            for campo, coordenadas in campos.items():
                
                pyautogui.moveTo(*coordenadas, duration=0)  
                pyautogui.click()
                
                if aba != 'aba3':
                    
                    pyautogui.typewrite(codigo_barras, interval=0)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(0.5)
                else:

                    time.sleep(0.5)
                    pyautogui.click(clicks=2, interval=0.5)
        

        os.system('cls')
        print("SO REALIZAR A BIPAGEM APOS ESSA MENSAGEM:")
        keyboard.wait("enter")

print("Pressione Enter para continuar...")
keyboard.wait("enter")

x, y = mostrar_coordenadas()
x2, y2 = mostrar_coordenadas()
x3, y3 = mostrar_coordenadas()

inserir_codigo(x, y, x2, y2, x3, y3)
