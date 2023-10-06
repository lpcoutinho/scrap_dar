from fastapi import FastAPI, Query, File, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from getDar import GetDar
import time
from loguru import logger
from utils import registrar_tempo_total
from fastapi.exceptions import HTTPException

# Configurar o logger para escrever logs em um arquivo chamado "app.log"
logger.add("app.log", rotation="500 MB", level="INFO")

app = FastAPI()

@app.get("/")
def read_root():
    # return {"message": "Bem-vindo ao Robô que captura DARs!","O scraper":"localhost/scrap"}
    # Caminho completo para o arquivo HTML que você deseja servir
    html_file_path = "templates/home.html"

    # Retorna o arquivo HTML usando FileResponse
    return FileResponse(html_file_path, media_type="text/html")

@app.post("/uploadfile/")
async def upload_file(file: UploadFile):
    try:
        # Verifique se o arquivo foi enviado
        if not file:
            raise HTTPException(status_code=400, detail="Nenhum arquivo foi enviado.")
        
        # Nome do arquivo original
        file_name = file.filename
        
        # Exemplo: Salvar o arquivo com seu nome original no diretório "uploads" no servidor
        with open(f"uploads/{file_name}", "wb") as f:
            f.write(file.file.read())
        
        # Redirecionar o usuário para outro endpoint após o processamento
        return RedirectResponse(url="/outro-endpoint/")
    
    except Exception as e:
        # Lidar com erros e exceções
        return HTTPException(status_code=500, detail=str(e))

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