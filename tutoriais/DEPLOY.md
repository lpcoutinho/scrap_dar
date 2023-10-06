# Robô DAR

## Deploy em AWS EC2

O Robô DAR é um aplicativo que coleta dados de DARs do Distrito Federal. Este tutorial mostra como realizar deploya do Robô DAR em uma instância EC2 da AWS.

### 1. Crie uma nova instância EC2

- Acesse o Console AWS e crie uma nova instância EC2 seguindo as configurações recomendadas.

### 2. Clone o repositório

```bash
# Clone o repositório do projeto
git clone https://github.com/lpcoutinho/scrap_dar.git
```

Caso queira encurtar o próximo passo navegue até o diretório do projeto e execute o script `./setup.sh`:

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Atualize e instale as dependências do projeto

```bash
# Atualize o sistema e instale as dependências necessárias
sudo apt-get update
sudo apt-get install -y wget gnupg unzip python3-venv xvfb nginx

# Baixe e instale o Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# Resolva possíveis dependências quebradas
sudo apt-get install -f

# Remova o arquivo de instalação do Chrome
rm google-chrome-stable_current_amd64.deb
```

### 4. Crie e ative um ambiente virtual

```bash
# Crie um ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate
```

### 5. Instale as bibliotecas do projeto

```bash
# Instale as bibliotecas Python necessárias
pip install -r requirements.txt
```

### 6. Configure o Nginx

Nginx é um servidor web que será usado para servir a API do Robô DAR.

- Crie o arquivo de configuração do Nginx:

```bash
sudo nano /etc/nginx/conf.d/fastapi.conf
```

- Edite o arquivo para configurar o proxy:

```nginx
server {
    listen 80;
    server_name <seu-endereço-de-IP-ou-DNS>;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 10800s; # Aumentar o tempo limite para resposta
    }
}
```

Lembre-se de substituir `<seu-endereço-de-IP-ou-DNS>` pelo endereço correto.

### 7. Reinicie o Nginx

```bash
# Recarregue a configuração do Nginx
sudo systemctl reload nginx
```

### 8. Crie diretórios necessários

Caso não tenha os diretórios *data, pdf e uploads* crie com:

```bash
mkdir data pdf uploads
```

### 9. Inicie a API

- Crie uma sessão Tmux para manter a API em execução:

```bash
# Crie uma sessão Tmux
tmux new -s fastapi
```

- Dentro da sessão Tmux, inicie a API usando o Xvfb:

```bash
xvfb-run uvicorn main:app --host 0.0.0.0 --port 8000
```

### Conclusão

A API do Robô DAR está agora disponível para utilização. Você pode acessá-la através do endereço IP ou DNS da sua instância EC2. Certifique-se de que sua instância EC2 tenha as portas 80 e 8000 abertas nas configurações de segurança do grupo.
