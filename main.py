from fastapi import FastAPI, Query
from getDar import GetDar
import time
from loguru import logger
from utils import registrar_tempo_total

# Configurar o logger para escrever logs em um arquivo chamado "app.log"
logger.add("app.log", rotation="500 MB", level="INFO")

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Robô que captura DARs!","O scraper":"localhost/scrap"}

@app.get("/scrap")
def scrap(dados: str = Query(..., title="Dados de Inscrições")):
    # Dividir a string em uma lista de inscrições usando vírgulas como separador
    lista_inscricoes = dados.split(',')

    # Registrar o tempo de início
    tempo_inicio = time.time()
    logger.info('Iniciar Raspagem de dados')

    # Use a função join para formatar a lista
    lista_formatada = ', '.join(lista_inscricoes)

    # Imprima a lista formatada
    print(f'* Os números de inscrição requeridos são: {lista_formatada}')

    getdar = GetDar()
    getdar.get_dar(numeros_inscricao=lista_inscricoes)

    # Calcular o tempo total gasto em toda a operação
    tempo_total = time.time() - tempo_inicio

    # Exibir o tempo total gasto
    logger.info(f"* Tempo total gasto em toda a operação: {tempo_total} segundos")

    # Registrar o tempo total e a hora atual usando a função em utils.py
    registrar_tempo_total(tempo_total)

    # Retornar uma resposta com as informações processadas
    return {"message": "Operação concluída com sucesso", "lista_inscricoes": lista_inscricoes}

