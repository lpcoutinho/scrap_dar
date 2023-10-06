from getDar import GetDar
import time
from loguru import logger

# Configurar o logger para escrever logs em um arquivo chamado "app.log"
logger.add("teste.log", rotation="500 MB", level="INFO")

# Registrar o tempo de início
tempo_inicio = time.time()
logger.warning('Iniciar Raspagem de dados')

lista = ['132465']
lista = ['51502038', '51502046', '51502054', '51502062']

# Use a função join para formatar a lista
lista_formatada = ', '.join(lista)

# Imprima a lista formatada
logger.info(f'Os números de inscrição requeridos são: {lista_formatada}')

getdar = GetDar()
getdar.get_dar(numeros_inscricao=lista)

# Calcular o tempo total gasto em toda a operação
tempo_total = time.time() - tempo_inicio

# Exibir o tempo total gasto
logger.info(f"Tempo total gasto em toda a operação: {tempo_total} segundos")

# Registrar o tempo total e a hora atual usando a função em utils.py
#registrar_tempo_total(tempo_total)
