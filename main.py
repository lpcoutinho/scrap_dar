from fastapi import FastAPI
from getDar import GetDar
import time
# from utils import registrar_tempo_total

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Robô que captura DARs!","O scraper":"localhost/scrap"}

@app.get("/scrap")
def scrap():
    
    # Registrar o tempo de início
    tempo_inicio = time.time()
    print(10*'*','Iniciar Raspagem de dados',10*'*')

    lista = ['132465']
    lista = ['51502038', '51502046', '51502054', '51502062']

    # Use a função join para formatar a lista
    lista_formatada = ', '.join(lista)

    # Imprima a lista formatada
    print(f'* Os números de inscrição requeridos são: {lista_formatada}')

    getdar = GetDar()
    getdar.get_dar(numeros_inscricao=lista)

    # Calcular o tempo total gasto em toda a operação
    tempo_total = time.time() - tempo_inicio

    # Exibir o tempo total gasto
    print(f"* Tempo total gasto em toda a operação: {tempo_total} segundos")

    # Registrar o tempo total e a hora atual usando a função em utils.py
    # registrar_tempo_total(tempo_total)
    
    return {"message": "Bem-vindo ao Robô que captura DARs!"}
