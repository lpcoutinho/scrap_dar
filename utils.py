import csv
import os
import zipfile
from datetime import datetime


def registrar_tempo_total(tempo_total, nome_arquivo="data/performance_total_time.csv"):
    """
    Registra o tempo total e a hora atual em um arquivo CSV.

    Args:
        tempo_total (float): O tempo total a ser registrado.
        nome_arquivo (str): O nome do arquivo CSV onde o tempo será registrado.
    """
    hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(nome_arquivo, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([hora_atual, tempo_total])


def zip_compress(directory_path, zip_file_path):
    """
    Comprime o conteúdo de uma pasta em um arquivo ZIP.

    Args:
        directory_path (str): O caminho para a pasta que você deseja comprimir.
        zip_file_path (str): O caminho completo para o arquivo ZIP de saída.

    Returns:
        None
    """
    try:
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory_path)
                    zipf.write(file_path, rel_path)

        print(f"Pasta '{directory_path}' comprimida com sucesso em '{zip_file_path}'")

    except Exception as e:
        print(f"Erro ao comprimir a pasta: {str(e)}")


def listar_arquivos_em_pasta(pasta):
    """
    Lista os nomes dos arquivos em uma pasta.

    Args:
        pasta (str): O caminho da pasta que deseja listar.

    Returns:
        List[str]: Uma lista contendo os nomes dos arquivos na pasta.
    """
    try:
        # Use a função listdir do módulo os para listar os arquivos na pasta
        arquivos = os.listdir(pasta)

        # Filtre apenas os arquivos (excluindo diretórios)
        arquivos = [
            arquivo
            for arquivo in arquivos
            if os.path.isfile(os.path.join(pasta, arquivo))
        ]

        return arquivos
    except Exception as e:
        print(f"Erro ao listar arquivos na pasta: {str(e)}")
        return []
