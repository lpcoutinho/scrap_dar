import urllib.request
import zipfile
import os
from pathlib import Path
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from loguru import logger
from fastapi.responses import FileResponse

# Configurar o logger para escrever logs em um arquivo chamado "app.log"
logger.add("app.log", rotation="500 MB", level="INFO")

pdf_dir = '/home/luiz/projects/scrap_dar/pdf'
# pdf_dir = '/home/ubuntu/scrap_dar/pdf'

class GetDar:
    def __init__(self):
        """
        Inicializa a classe GetDar.

        A classe é inicializada sem nenhum número de inscrição. Ela também cria dois DataFrames vazios para armazenar dados.
        - O DataFrame `dados_df` é usado para armazenar informações sobre DARs.
        - O DataFrame `dados_performance` é usado para rastrear o desempenho de diferentes etapas do processo.
        """
        self.driver = None
        self.dados_df = pd.DataFrame(columns=['Inscricao', 'Ano', 'DAR', 'Nome', 'Endereço', 'Cota', 'Valor', 'Multa', 'Juros', 'Outros', 'ValorTotal', 'Cod_Barras', 'PDF_Name'])
        self.dados_performance = pd.DataFrame(columns=['Download_plugin', 'Resolve_Captcha', 'Consulta_DAR', 'Get_DAR', 'Scrap_Time', 'Total_Parcial'])
        self.dados_performance_total_time = pd.DataFrame(columns=['Data','Total_time'])
        
        logger.info("Verificando arquivos CSV")
        
        dados_csv = 'data/dados.csv'
        if not os.path.exists(dados_csv):
            self.dados_df.to_csv(dados_csv, index=False)
            logger.info(f"{dados_csv} criado com sucesso!")
        logger.info(f"{dados_csv} verificado!")
        
        performance_csv = 'data/performance.csv'
        if not os.path.exists(performance_csv):
            self.dados_performance.to_csv(performance_csv, index=False)
            logger.info(f"{dados_csv} criado com sucesso!")
        logger.info(f"{dados_csv} verificado!")
        
        total_time_csv = 'data/performance_total_time.csv'
        if not os.path.exists(total_time_csv):
            self.dados_performance_total_time.to_csv(total_time_csv, index=False)
            logger.info(f"{total_time_csv} criado com sucesso!")
        logger.info(f"{total_time_csv} verificado!")

    def init_driver(self):
        """
        Inicializa o driver do Chrome para a automação do scraping.

        Este método realiza as seguintes etapas:
        1. Registra o tempo de início da inicialização do driver.
        2. Baixa o plugin anti-captcha a partir de uma URL.
        3. Descompacta o arquivo do plugin.
        4. Define a chave da API no arquivo de configuração do plugin.
        5. Cria um arquivo zip do diretório do plugin para uso posterior.
        6. Registra o tempo de download do plugin.
        7. Configura as opções de inicialização do navegador Chrome.
        8. Inicializa o driver do Chrome com as opções configuradas.

        Returns:
            float: O tempo em segundos para baixar o plugin.
        """
        init_driver_time = time.time() 

        plugin = "plugin/"

        if os.path.exists(plugin) and os.path.isdir(plugin):
            # O diretório existe, então você pode realizar a ação desejada aqui.
            logger.info('Plugin já baixado.')
        else:
            logger.info('Baixando plugin.')

            # Baixa o plugin anti-captcha
            url = 'https://antcpt.com/anticaptcha-plugin.zip'
            filehandle, _ = urllib.request.urlretrieve(url)
            
            logger.info('Descompactando e instalando plugin.')
            # Descompacta o arquivo do plugin
            with zipfile.ZipFile(filehandle, "r") as f:
                f.extractall("plugin")
        
        # Define a chave da API no arquivo de configuração do plugin
        api_key = "3f6496391630e35dff64c09607c4b729"
        file = Path('./plugin/js/config_ac_api_key.js')
        file.write_text(file.read_text().replace("antiCapthaPredefinedApiKey = ''", "antiCapthaPredefinedApiKey = '{}'".format(api_key)))
        
        # Cria um arquivo zip do diretório do plugin para uso posterior
        zip_file = zipfile.ZipFile('./plugin.zip', 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk("./plugin"):
            for file in files:
                path = os.path.join(root, file)
                zip_file.write(path, arcname=path.replace("./plugin/", ""))
        zip_file.close()

        # Registra o tempo de download do plugin
        tempo_apos_download_plugin = time.time()
        self.tempo_download_plugin = tempo_apos_download_plugin - init_driver_time
        
        logger.info(f"Tempo para instalar o plugin: {self.tempo_download_plugin} segundos")
        logger.info('Configurando o Chrome.')
        
        # Configura as opções de inicialização do navegador Chrome
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_extension('./plugin.zip')
        prefs = {
            # "download.default_directory": "/pdf",  # Define o diretório padrão de download
            "download.default_directory": f"{pdf_dir}",  # Define o diretório padrão de download
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        }
        options.add_experimental_option("prefs", prefs)
        
        # options.add_argument(r"--user-data-dir=/home/luiz/.config/google-chrome/")
        # options.add_argument(r'--profile-directory=Default')
        
        # Inicializa o driver do Chrome com as opções configuradas
        self.driver = webdriver.Chrome(options=options)
        
        tempo_apos_chrome_config = time.time()
        self.tempo_chrome_config = tempo_apos_chrome_config - tempo_apos_download_plugin
        
        logger.info(f"Tempo para configurar o Chrome: {self.tempo_chrome_config} segundos")
        logger.info('Iniciando o Chrome.')
        
        return self.tempo_download_plugin, self.tempo_chrome_config

    def close_driver(self):
        """
        Encerra o driver do Chrome.
        """
        logger.info('Encerrando driver.')
        
        if self.driver:
            self.driver.quit()

    def change_exercicio(self):
        """
        Altera o exercício para um ano anterior no site da Receita Federal do Distrito Federal.

        Este método realiza as seguintes etapas:
        1. Localiza o elemento de seleção do exercício usando um XPath.
        2. Clica no elemento de seleção para abrir o menu suspenso.
        3. Localiza e clica na opção do exercício anterior no menu suspenso.

        Returns:
            None
        """
        logger.info('Alterando ano de exercício.')
        
        # Localiza o elemento de seleção do exercício usando XPath
        select_exec_xpath = '//*[@id="mat-select-value-1"]'
        select_exec = self.driver.find_element(By.XPATH, select_exec_xpath)
        
        # Clica no elemento de seleção para abrir o menu suspenso
        select_exec.click()
        
        # Localiza e clica na opção do exercício anterior no menu suspenso
        exec_ant_xpath = '//*[@id="mat-option-1"]'
        exec_ant = self.driver.find_element(By.XPATH, exec_ant_xpath)
        exec_ant.click()

    def show_data(self,inscricao,exercicio):
        """
        Mostra os dados da classe, incluindo o número de inscrição, exercício e performance.

        Returns:
            None
        """
        logger.warning(f'Raspagem dos dados de {inscricao} completa!')
        logger.info(f"Número de inscrição: {inscricao}")
        logger.info(f'Exercício: {exercicio}')
        logger.info(f"Tempo para baixar o plugin: {self.tempo_download_plugin} segundos")
        logger.info(f"Tempo para configurar o Chrome: {self.tempo_chrome_config} segundos")
        logger.info(f"Tempo para resolver o Captcha: {self.tempo_resolucao_captcha} segundos")

    def atualizar_dados(self, novos_dados):
        """
        Adiciona novos dados ao DataFrame e atualiza o CSV.

        Args:
            novos_dados (list of dict): Uma lista de dicionários com novos dados a serem adicionados.

        Returns:
            None
        """
        logger.info('Atualizando dados.')
        
        # Adicione os novos dados ao DataFrame
        novos_dados = pd.concat([self.dados_df, pd.DataFrame([novos_dados])], ignore_index=True).drop_duplicates()
            
        # Salve o DataFrame no arquivo CSV
        novos_dados.to_csv('data/dados.csv', index=False, sep=';', mode='a', header=False)
      
    def atualizar_performance(self, nova_performance):
        """
        Adiciona novos dados ao DataFrame e atualiza o CSV.

        Args:
            nova_performance (list of dict): Uma lista de dicionários com novos dados a serem adicionados.

        Returns:
            None
        """
        logger.info('Atualizando dados de performance.')
        
        # Adicione os novos dados ao DataFrame
        self.dados_performance = pd.concat([self.dados_performance, pd.DataFrame([nova_performance])], ignore_index=True).drop_duplicates()
            
        # Salve o DataFrame no arquivo CSV
        self.dados_performance.to_csv('data/performance.csv', index=False, sep=';', mode='a', header=False)

    def fill_and_scrape(self, inscricao):
        """
        Preenche o número de inscrição e realiza o scraping.

        Args:
            inscricao (str): O número de inscrição a ser preenchido.

        Returns:
            None
        """
        logger.info(f'Raspando dados de: {inscricao}')
        
        try:
            init = time.time()
            
            inscricao_xpath = '//*[@id="mat-input-0"]'
            inscricao_input = self.driver.find_element(By.XPATH, inscricao_xpath)
            inscricao_input.clear()
            inscricao_input.send_keys(inscricao)
            time.sleep(2)  # Aguarde para que os resultados sejam carregados (ajuste conforme necessário)
            
            logger.info(f'Resolvendo o captcha')
            # Aguardar pelo seletor "solved" para subir
            WebDriverWait(self.driver, 120).until(lambda x: x.find_element(By.CSS_SELECTOR,'.antigate_solver.solved'))

            # Registrar o tempo após a resolução do Captcha
            tempo_apos_resolucao_captcha = time.time()

            self.tempo_resolucao_captcha = tempo_apos_resolucao_captcha - init
            logger.info(f"Tempo para resolver o Captcha: {self.tempo_resolucao_captcha} segundos")
        except Exception as e:
            logger.error(f'Erro na resolução do captcha:', e)
            print("O tipo do erro é:", type(e))
            # self.driver.save_screenshot('ERROR_captcha.png')

        try:
            # Botão "Consultar"
            botao_xpath='//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-footer/button'
            botao_consultar = self.driver.find_element(By.XPATH, botao_xpath)
            botao_consultar.click()
            
            # Registrar o tempo após clicar no botão "Consultar"
            tempo_apos_clicar_consultar = time.time()
            
            # Aguardar um pouco para a página carregar
            time.sleep(2)

            tempo_apos_esperar_consultar = time.time()

            self.tempo_consulta = tempo_apos_esperar_consultar - tempo_apos_clicar_consultar
            logger.info(f"Tempo para Consultar: {self.tempo_consulta} segundos")

            try:
                no_dar_box_tag = 'simple-snack-bar'                        
                # no_dar_box = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME, no_dar_box_tag)))
                no_dar_box = self.driver.find_element(By.TAG_NAME, no_dar_box_tag)
                no_dar_box_text = no_dar_box.text.strip()
                # logger.info("Texto do elemento visível:", no_dar_box_text)            
                
                try:
                    ano_element = self.driver.find_element(By.XPATH, '//*[@id="mat-select-value-1"]/span/span')
                    ano_output = ano_element.text
                except:
                    ano_element = self.driver.find_element(By.XPATH, '//*[@id="mat-select-value-1"]/span/span')
                    ano_output = ano_element.text
                
                novos_dados = {'* Inscricao': inscricao ,'Ano': ano_output, 'DAR': False, 'Nome': None, 'Endereço': None, 'Cota': None, 'Valor': None, 'Multa': None, 'Juros': None, 'Outros': None, 'ValorTotal': None, 'Cod_Barras': None, 'PDF_Name': None}

                # Atualizar o arquivo CSV
                self.atualizar_dados(novos_dados)
                
                end = time.time()
                
                scrap_time = (end - init)
                total_parcial = scrap_time + self.tempo_download_plugin
                performance = {'* Download_plugin':self.tempo_download_plugin, 'Resolve_Captcha': self.tempo_resolucao_captcha, 'Consulta_DAR': self.tempo_consulta, 'Get_DAR': None, 'Scrap_Time':scrap_time, 'Total_Parcial': total_parcial}
                self.atualizar_performance(performance)
                performance = {}
                
            except:                 
                # XPath para os elementos de informações
                inscricao = '//*[@id="InfoCabecalho"]/mat-card/mat-card-content/shared-description-list/shared-term[1]/div'
                nome = '//*[@id="InfoCabecalho"]/mat-card/mat-card-content/shared-description-list/shared-term[2]/div'
                endereco = '//*[@id="InfoCabecalho"]/mat-card/mat-card-content/shared-description-list/shared-term[3]/div'

                # Capturar informações de inscrição, nome e endereço
                inscricao_output = self.driver.find_element(By.XPATH,inscricao).text.strip()
                nome_output = self.driver.find_element(By.XPATH,nome).text.strip()
                endereco_output = self.driver.find_element(By.XPATH,endereco).text.strip()
                
                # Encontrar todos os elementos com a classe "mat-accent shared-card-item ng-star-inserted"
                elementos = self.driver.find_elements(By.TAG_NAME, "mat-row")

                # Inicialize uma variável de índice
                indice = 1
                
                # Iterar sobre cada elemento encontrado
                for elemento in elementos:
                    logger.info(f"* Linha: {indice}")

                    # Crie o XPath dinamicamente com base no índice
                    xpath_ano = f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{indice}]/mat-cell[1]'
                    xpath_cota = f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{indice}]/mat-cell[2]'
                    xpath_valor = f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{indice}]/mat-cell[3]'
                    xpath_multa = f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{indice}]/mat-cell[4]'
                    xpath_juros = f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{indice}]/mat-cell[5]'
                    xpath_outros = f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{indice}]/mat-cell[6]'
                    xpath_valor_total = f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{indice}]/mat-cell[7]'
                    xpath_cod_button = f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{indice}]/mat-cell[8]/app-copy-to-clipboard-botao/button'
                    xpath_pdf_button = f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{indice}]/mat-cell[8]/button[2]'
                    xpath_cod_fechar = '//span[text()="Fechar"]/ancestor::button'

                    # Pegar o ano
                    ano_element = elemento.find_element(By.XPATH, xpath_ano)
                    ano_output = ano_element.text.strip()

                    # Pegar a cota e substituir espaços e barras por underscores
                    cota_element = elemento.find_element(By.XPATH, xpath_cota)
                    cota_output = cota_element.text.strip()
                    cota_output = cota_output.replace(' ', '_')
                    cota_output = cota_output.replace('/', '_')

                    # Pegar o valor, multa, juros, outros e valor total
                    valor_element = elemento.find_element(By.XPATH, xpath_valor)
                    valor_output = valor_element.text.strip()
                    multa_element = elemento.find_element(By.XPATH, xpath_multa)
                    multa_output = multa_element.text.strip()
                    juros_element = elemento.find_element(By.XPATH, xpath_juros)
                    juros_output = juros_element.text.strip()
                    outros_element = elemento.find_element(By.XPATH, xpath_outros)
                    outros_output = outros_element.text.strip()
                    valor_total_element = elemento.find_element(By.XPATH, xpath_valor_total)
                    valor_total = valor_total_element.text.strip()

                    logger.info(f'* Inscrição: {inscricao_output}')
                    logger.info(f'* Razão social: {nome_output}')
                    logger.info(f'* Ano: {ano_output}')
                    logger.info(f'* Endereço: {endereco_output}')

                    logger.info(f'Pegando PDF {indice}')
                    # Download PDF
                    pdf_element = elemento.find_element(By.XPATH, xpath_pdf_button)
                    pdf_element.click()
                    time.sleep(1)
                    
                    logger.info('Pegando código de barras')
                    # Cod Barras
                    cod_bar_button = elemento.find_element(By.XPATH, xpath_cod_button)
                    cod_bar_button.click()
                    time.sleep(1)
                    
                    try:
                        class_cod_bar = 'mat-dialog-content'
                        cod_bar_element = self.driver.find_element(By.CLASS_NAME,class_cod_bar)
                        cod_bar_output = cod_bar_element.text.strip()
                    except Exception as e:
                        logger.error("Ocorreu um erro:", e)
                        logger.error("O tipo do erro é:", type(e))
                        logger.error(f'* Não pegou com: 1 {class_cod_bar}')
                        try:
                            class_cod_bar = "mat-dialog-content"
                            cod_bar_element = self.driver.find_element(By.CLASS_NAME, class_cod_bar)
                            cod_bar_output = cod_bar_element.text.strip()
                        except Exception as e:
                            logger.error("Ocorreu um erro:", e)
                            logger.error("O tipo do erro é:", type(e))
                            logger.error(f'* Não pegou com: 2 {class_cod_bar}')
                            try:
                                class_cod_bar = "mat-dialog-content.mat-dialog-content"
                                cod_bar_element = self.driver.find_element(By.CSS_SELECTOR, class_cod_bar)
                                cod_bar_output = cod_bar_element.text.strip()
                            except Exception as e:
                                logger.error("Ocorreu um erro:", e)
                                logger.error("O tipo do erro é:", type(e))
                                logger.error(f'* Não pegou com: 3 {class_cod_bar}')
                                try:
                                    class_cod_bar = '//mat-dialog-content'
                                    cod_bar_element = self.driver.find_element(By.XPATH, class_cod_bar)
                                    cod_bar_output = cod_bar_element.text.strip()
                                except Exception as e:
                                    logger.error("Ocorreu um erro:", e)
                                    logger.error("O tipo do erro é:", type(e))
                                    logger.error(f'* Não pegou com: 4 {class_cod_bar}')

                                # Encontre o índice onde o texto deve ser cortado
                                text_remove = "O número do código de barras referente ao débito selecionado, já foi copiado para área de transferência."
                                indice_inicio = cod_bar_output.find(text_remove)

                                # Verifique se o texto foi encontrado
                                if indice_inicio != -1:
                                    # Remova o texto encontrado e qualquer espaço em branco subsequente
                                    cod_bar_output = cod_bar_output[indice_inicio + len(text_remove):].strip()
                                else:
                                    # Caso o texto não tenha sido encontrado, mantenha o texto original
                                    cod_bar_output = cod_bar_output
                                    
                    # Encontre o índice onde o texto deve ser cortado
                    text_remove = "O número do código de barras referente ao débito selecionado, já foi copiado para área de transferência."
                    indice_inicio = cod_bar_output.find(text_remove)

                    # Verifique se o texto foi encontrado
                    if indice_inicio != -1:
                        # Remova o texto encontrado e qualquer espaço em branco subsequente
                        cod_bar_output = cod_bar_output[indice_inicio + len(text_remove):].strip()
                    else:
                        # Caso o texto não tenha sido encontrado, mantenha o texto original
                        cod_bar_output = cod_bar_output

                    botao_fechar = self.driver.find_element(By.XPATH, xpath_cod_fechar)
                    botao_fechar.click()
                    time.sleep(2)
                    
                    logger.info('Renomeando arquivo PDF')
                    # Gerar o nome do arquivo PDF com base nas informações
                    nome_arquivo_pdf = f"{pdf_dir}/{inscricao_output}_{ano_output}_{cota_output}.pdf"

                    # Renomear o arquivo PDF após o download
                    novo_nome = os.rename(f"{pdf_dir}/RelatorioDAR.pdf", nome_arquivo_pdf)
                    
                    print(novo_nome)    
                    FileResponse(novo_nome, filename='teste.pdf')
                    
                    novos_dados = {'Inscricao': inscricao_output ,'Ano': ano_output, 'DAR': True,'Nome': nome_output, 'Endereço': endereco_output, 'Cota': cota_output, 'Valor': valor_output, 'Multa': multa_output, 'Juros': juros_output, 'Outros': outros_output, 'ValorTotal': valor_total, 'Cod_Barras': cod_bar_output, 'PDF_Name': nome_arquivo_pdf}
                    # Atualizar o arquivo CSV
                    self.atualizar_dados(novos_dados)
                    
                    # Incrementar o índice para a próxima iteração
                    indice += 1
                
                end = time.time()
                
                scrap_time = (end - init)
                total_parcial = scrap_time + self.tempo_download_plugin
                performance = {'Download_plugin':self.tempo_download_plugin, 'Resolve_Captcha': self.tempo_resolucao_captcha, 'Consulta_DAR': self.tempo_consulta, 'Get_DAR': None, 'Scrap_Time':scrap_time, 'Total_Parcial': total_parcial}
                self.atualizar_performance(performance)
                
            return self.tempo_resolucao_captcha, self.tempo_consulta
        
        except Exception as e:
            logger.info(f"Ocorreu um erro ao processar a inscrição {inscricao_output}: {str(e)}")

    def get_dar(self, numeros_inscricao):
        """
        Realiza o scraping do site da Receita Federal do Distrito Federal para obter o DAR (Documento de Arrecadação de Receitas)
        para uma lista de números de inscrição.

        Args:
            numeros_inscricao (list): Uma lista de números de inscrição para os quais o scraping será feito.

        Returns:
            None
        """
        try:
            self.init_driver()
            url = "https://ww1.receita.fazenda.df.gov.br/emissao-segunda-via/iptu"
            
            for inscricao in numeros_inscricao:
                self.driver.get(url)
                # self.driver.save_screenshot('init_chrome.png')
                try:
                    self.fill_and_scrape(inscricao)
                    self.show_data(inscricao,'2023')
                    time.sleep(3)
                except Exception as e:
                    print("Ocorreu um erro:", e)
                    print("O tipo do erro é:", type(e))
                    pass
                
                
                # self.driver.get(url)
                # try:
                #     self.change_exercicio()
                #     self.fill_and_scrape(inscricao)
                #     self.show_data(inscricao,'anteriores')
                #     time.sleep(3)
                # except Exception as e:
                    print("Ocorreu um erro:", e)
                    print("O tipo do erro é:", type(e))
                #     pass
                
        finally:
            self.close_driver()
