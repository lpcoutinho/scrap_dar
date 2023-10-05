# Use a imagem base oficial do Python
FROM python:3.10-slim

# Instale as dependências do sistema, incluindo o Google Chrome
RUN apt-get update && apt-get install -y wget gnupg unzip && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Configurar o diretório de trabalho
WORKDIR /app

# Copiar o código da aplicação
COPY . .

# Instalar as dependências Python
RUN pip install -r requirements.txt

# Expor a porta desejada
EXPOSE 80

# Comando de inicialização da aplicação com Uvicorn
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]
