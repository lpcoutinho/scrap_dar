# Robô DAR

## Deploy em AWS EC2

1. Crie uma nova instância EC2
2. Atualize e instale as dependências do projeto

    ```bash
    sudo apt-get update 
    sudo apt-get install -y wget gnupg unzip python3-venv xvfb nginx
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb 
    sudo dpkg -i google-chrome-stable_current_amd64.deb 
    sudo apt-get install -f
    rm google-chrome-stable_current_amd64.deb
    ```

3. Clone o repositório:

    ```bash
    git clone https://github.com/lpcoutinho/scrap_dar.git
    ```

4. Crie e ative um ambiente virtual

    ```bash
    python3 -m venv venv
    . venv/bin/activate
    ```

5. Instale as bibliotecas do projeto

    ```bash
    pip install -r requirements.txt
    ```

6. Inicie a API

    ```bash
    xvfb-run uvicorn main:app --host 0.0.0.0 --port 8000
    ```

7. Configure Nginx

    Crie o arquivo de configuração

    ```bash
    sudo nano /etc/nginx/conf.d/fastapi.conf
    ```

    Edite

    ```bash
    server {
        listen 80;
        server_name 52.91.224.206;
    
        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
    ```

8. Reinicie Nginx

    ```bash
    
    ```

9. Crie um terminal Tmux e rode a api dentro dele

    ```bash
    
    ```

10. Texto

    ```bash
    
    ```
