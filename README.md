# Robô DAR

## Deploy em AWS EC2

1. Crie uma nova instância EC2
2. Instale docker. [Tutorial oficial.](https://docs.docker.com/engine/install/ubuntu/)
3. Intale docker compose. [Tutorial oficial](https://docs.docker.com/compose/install/linux/)
4. Caso tenha problemas de permissão [acesse este tutorial.](https://www.baeldung.com/linux/docker-permission-denied-daemon-socket-error)
5. Clone o repositório:

    ```bash
    git clone https://github.com/lpcoutinho/scrap_dar.git
    ```

6. Caminhe até o novo diretório e construa o contêiner Docker usando o seguinte comando:

    ```bash
    docker build -t scraper .
    ```

7. Execute o contêiner com Docker compose o seguinte comando:

    ```bash
    docker compose up -d
    ```

    - Caso queira executar apenas o container

        ```bash
        docker run -d -p 80:80 scraper
        ```

8. Se tudo está ok você pode verificar o container com o comando:

    ```bash
    docker ps
    ```

    ```bash
    ```

    ```bash
    ```
