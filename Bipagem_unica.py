import pyautogui
import keyboard
import time

def inserir_codigo():
    coordenadas_abas = {
        'aba1': {'campo1': (334, 61), 'campo2': (334, 61)},
        'aba2': {'campo1': (1606, 1009), 'campo2': (1606, 1009)},
        'aba3': {'campo1': (1433, 430)}
    }
    
    while True:
        codigo_barras = input("Insira o código de barras e pressione Enter (ou digite 'sair' para sair): ")
        
        if codigo_barras.lower() == 'sair':
            print("Saindo do programa.")
            break

        if len(codigo_barras) < 1:
            print("Código de barras inválido. Insira um código com pelo menos 1 caractere.")
            continue

        for aba, campos in coordenadas_abas.items():
            for campo, coordenadas in campos.items():
                
                pyautogui.moveTo(coordenadas, duration=0)
                pyautogui.click()
                
                if aba != 'aba3':
                    
                    pyautogui.typewrite(codigo_barras, interval=0)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(0.5)
                else:
                   
                    time.sleep(0.5)
                    pyautogui.click()
                    time.sleep(0.5)
        
        print("Código inserido. Pressione Enter para inserir outro código ou digite 'sair' para sair.")
        keyboard.wait("enter")


inserir_codigo()
