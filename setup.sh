#!/bin/bash

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

# Cria os diretórios necessários para o projeto
mkdir data pdf uploads

# Informe que a instalação foi concluída
echo "Instalação concluída com sucesso!"
