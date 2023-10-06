import csv
from datetime import datetime

def registrar_tempo_total(tempo_total, nome_arquivo='data/performance_total_time.csv'):
    """
    Registra o tempo total e a hora atual em um arquivo CSV.

    Args:
        tempo_total (float): O tempo total a ser registrado.
        nome_arquivo (str): O nome do arquivo CSV onde o tempo será registrado.
    """
    hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(nome_arquivo, mode='a', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([hora_atual, tempo_total])
