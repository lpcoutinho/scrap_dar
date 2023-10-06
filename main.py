from fastapi import FastAPI, Query, File, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from getDar import GetDar
import time
from loguru import logger
from utils import registrar_tempo_total
from fastapi.exceptions import HTTPException
import pandas as pd
import os

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

# @app.post("/uploadfile")
@app.post("/uploadfile") 
async def upload_file(file: UploadFile):
    html_file_path = "templates/consultar.html"
    try:
        # Verifique se o arquivo foi enviado
        if not file:
            raise HTTPException(status_code=400, detail="Nenhum arquivo foi enviado.")
        
        # Gerar um nome de arquivo único com base no horário atual
        new_file_name = f"uploads/consulta.xlsx"
        
        # Salvar o arquivo com o novo nome
        with open(new_file_name, "wb") as f:
            f.write(file.file.read())
        
        # Retorna o novo nome de arquivo
        # return {"message": f"Arquivo '{new_file_name}' enviado com sucesso"}
        return FileResponse(html_file_path, media_type="text/html")
        
    
    except Exception as e:
        # Lidar com erros e exceções
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        # Lidar com erros e exceções
        return HTTPException(status_code=500, detail=str(e))

@app.get("/scrap")
def scrap():
    try:
        # Verifique se 'dados' contém um caminho de arquivo válido
        excel_file_path = f"uploads/consulta.xlsx"  # Caminho completo para o arquivo Excel na pasta 'uploads'
        print(excel_file_path)
        # Verifique se o arquivo existe
        if not os.path.exists(excel_file_path):
            raise HTTPException(status_code=404, detail="O arquivo Excel não foi encontrado.")
        print('existe arquivo')
        # Carregue o arquivo Excel usando Pandas
        df = pd.read_excel(excel_file_path)  # Leia o arquivo Excel
        lista_inscricoes = df['Inscrições'].tolist()  # Extraia a coluna como uma lista

        print(lista_inscricoes)
        
         # Registrar o tempo de início
        tempo_inicio = time.time()
        logger.info('Iniciar Raspagem de dados')

        # Verifique se a coluna 'Inscrições' existe no DataFrame
        if 'Inscrições' in df.columns:
            lista_inscricoes = df['Inscrições'].astype(str).tolist()  # Converta para strings e extraia a coluna como uma lista
            # Use a função join para formatar a lista
            lista_formatada = ', '.join(lista_inscricoes)
            print(f'* Os números de inscrição requeridos são: {lista_formatada}')

        getdar = GetDar()
        getdar.get_dar(numeros_inscricao=lista_inscricoes)

        # Calcular o tempo total gasto em toda a operação
        tempo_total = time.time() - tempo_inicio

        # Exibir o tempo total gasto
        logger.info(f"* Tempo total gasto em toda a operação: {tempo_total} segundos")

        # Registrar o tempo total e a hora atual usando a função em utils.py
        registrar_tempo_total(tempo_total)

        # Após a leitura dos dados, remova o arquivo Excel
        os.remove(excel_file_path)

        # Resto do código permanece o mesmo

        # Retornar uma resposta com as informações processadas
        return {"message": "Operação concluída com sucesso", "lista_inscricoes": lista_inscricoes}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="O arquivo Excel não foi encontrado.")
    except Exception as e:
        # Lidar com outros erros e exceções
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
