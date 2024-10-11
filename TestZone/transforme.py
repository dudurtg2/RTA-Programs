import json
import requests

# Carrega o arquivo JSON contendo as cidades
with open('cidades_com_ceps.json', 'r', encoding='utf-8') as f:
    cidades = json.load(f)

# URL do endpoint onde os dados serão enviados
url = "http://localhost:8080/cidades/save"

# Envia cada cidade individualmente como uma requisição POST
for cidade in cidades:
    response = requests.post(url, json=cidade)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 201:
        print(f"Cidade {cidade['nome']} enviada com sucesso!")
    else:
        print(f"Falha ao enviar a cidade {cidade['nome']}. Status Code: {response.status_code}")

