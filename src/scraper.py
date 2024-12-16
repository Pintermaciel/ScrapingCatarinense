import os
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from src.models.categoria import Categoria
from src.models.grupo import Grupo
from src.models.produto import Produto
from src.models.subgrupo import Subgrupo
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PageNavigator:
    """
    Uma classe para navegar em páginas da web usando Selenium.
    """

    def __init__(self):
        """
        Inicializa o WebDriver do Chrome com opções headless.

        Returns:
            None
        """
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def get(self, url):
        """
        Navega para a URL especificada.

        Args:
            url (str): A URL para a qual navegar.

        Returns:
            str: Mensagem de confirmação se bem-sucedido, ou mensagem de erro se ocorrer um erro.

        Raises:
            Exception: Se ocorrer um erro ao navegar para a URL.
        """
        try:
            self.driver.get(url)
            return logger.info(f'Navegou para a URL: {url}')
        except Exception as e:
            return logger.error(f'Erro ao navegar para a URL: {e}')

    def find_element_and_click(self, css_selector):
        """
        Encontra um elemento pelo seu seletor CSS e clica nele.

        Args:
            css_selector (str): O seletor CSS do elemento a ser clicado.

        Returns:
            str: Mensagem de confirmação se bem-sucedido, ou mensagem de erro se ocorrer um erro.

        Raises:
            Exception: Se ocorrer um erro ao encontrar ou clicar no elemento.
        """
        try:
            wait = WebDriverWait(self.driver, 10)
            element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
            element.click()
            return logger.info(
                f'Clicou no elemento com o seletor CSS: {css_selector}'
            )
        except Exception as e:
            return logger.error(f'Erro ao clicar no elemento: {e}')

    def quit(self):
        """
        Encerra o WebDriver e fecha o navegador.

        Returns:
            str: Mensagem de confirmação indicando que o WebDriver foi fechado.
        """
        self.driver.quit()
        return 'WebDriver fechado com sucesso.'


class Scraper:
    """
    Uma classe para raspar dados de uma página da web.
    """

    def __init__(self, url):
        """
        Inicializa o Scraper com a URL alvo.

        Args:
            url (str): A URL da página a ser raspada.
        """
        self.url = url
        self.css_grupos = os.getenv(
            'CSS_GRUPOS', 'ul.submenu-scroll li[data-menu]'
        )
        self.navigator = PageNavigator()

    def fetch_html(self):
        """
        Obtém o conteúdo HTML da URL alvo.

        Este método navega para a URL alvo, aguarda a presença de um elemento
        com o seletor CSS especificado na variável de ambiente CSS_GRUPOS, e
        retorna o conteúdo HTML da página.

        Returns:
            tuple: Uma tupla contendo o conteúdo HTML da página e uma mensagem de confirmação,
                ou uma mensagem de erro se ocorrer um erro.

        Raises:
            Exception: Se ocorrer um erro ao obter o conteúdo HTML.
        """
        self.navigator.get(self.url)
        try:
            WebDriverWait(self.navigator.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.css_grupos)
                )
            )
            html = self.navigator.driver.page_source
            return html, logger.info(f'HTML obtido com sucesso')
        except Exception as e:
            logger.error(f'Erro ao obter HTML: {e}')
            return None, logger.error(f'Erro ao obter HTML: {e}')

    def get_grupos(self, html):
        """
        Extrai grupos do conteúdo HTML.

        Args:
            html (str): O conteúdo HTML do qual extrair grupos.

        Returns:
            tuple: Uma tupla contendo um dicionário de objetos Grupo e uma mensagem de confirmação,
                ou uma mensagem de erro se ocorrer um erro.

        Raises:
            Exception: Se ocorrer um erro ao extrair grupos.
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            grupos = soup.select('li[data-menu]')

            grupos_objetos = {}
            for grupo in grupos:
                try:
                    tag_a = grupo.find('a')
                    if tag_a:
                        descricao = tag_a.get_text(strip=True)
                        link = tag_a['href']
                        grupos_objetos[descricao.lower()] = Grupo(
                            descricao=descricao, link=link
                        )
                except KeyError as e:
                    logger.error(f'Erro ao processar grupo: {e}')
                except Exception as e:
                    logger.error(
                        f"""Erro inesperado ao processar grupo:
                        {e}"""
                    )

            for g in grupos_objetos:
                print(f'grupo: {g}')

            return grupos_objetos, logger.info(f'Grupos extraídos com sucesso')
        except Exception as e:
            logger.error(f'Erro ao extrair grupos: {e}')
            return None, logger.error(f'Erro ao extrair grupos: {e}')

    def get_subgrupos(self, html, grupos_objetos):
        """
        Extrai subgrupos do conteúdo HTML.

        Args:
            html (str): O conteúdo HTML do qual extrair subgrupos.
            grupos_objetos (dict): Um dicionário de objetos Grupo.

        Returns:
            tuple: Uma tupla contendo um dicionário de objetos Subgrupo e uma mensagem de confirmação,
                ou uma mensagem de erro se ocorrer um erro.

        Raises:
            Exception: Se ocorrer um erro ao extrair subgrupos.
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            subgrupos_objetos = {}

            grupos_nome_map = {
                grupo.descricao.lower(): grupo
                for grupo in grupos_objetos.values()
            }

            for subgrupo in soup.select('div.submenu.submenu--level-2'):
                for li in subgrupo.find_all(
                    'li', class_='submenu__item submenu__item--main'
                ):
                    tag_a = li.find('a')
                    if tag_a:
                        descricao = tag_a.get_text(strip=True)
                        link = tag_a['href']

                        grupo_nome = next(
                            (
                                grupo
                                for nome, grupo in grupos_nome_map.items()
                                if nome in link.lower()
                            ),
                            None,
                        )

                        if grupo_nome:
                            subgrupos_objetos[descricao.lower()] = Subgrupo(
                                descricao=descricao,
                                link=link,
                                grupo=grupo_nome,
                            )

            for s in subgrupos_objetos:
                print(f'subgrupo: {s}')
            return subgrupos_objetos, logger.info(
                f'Subgrupos extraídos com sucesso'
            )

        except Exception as e:
            logger.error(f'Erro ao extrair subgrupos: {e}')
            return None, logger.error(f'Erro ao extrair subgrupos: {e}')

    def get_categorias(self, html, subgrupos_objetos):
        """
        Extrai categorias do conteúdo HTML.

        Args:
            html (str): O conteúdo HTML do qual extrair categorias.
            subgrupos_objetos (dict): Um dicionário de objetos Subgrupo.

        Returns:
            tuple: Uma tupla contendo um dicionário de objetos Categoria e uma mensagem de confirmação,
                ou uma mensagem de erro se ocorrer um erro.

        Raises:
            Exception: Se ocorrer um erro ao extrair categorias.
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            categorias_objetos = {}

            subgrupos_nome_map = {
                subgrupo.descricao.lower(): subgrupo
                for subgrupo in subgrupos_objetos.values()
            }

            for categoria in soup.select('div.submenu.submenu--level-3'):
                for li in categoria.find_all('li', class_='submenu__item'):
                    tag_a = li.find('a')
                    if tag_a:
                        descricao = tag_a.get_text(strip=True)
                        link = tag_a.get('href')

                        # Procurar o subgrupo correspondente
                        subgrupo_nome = next(
                            (
                                subgrupo
                                for nome, subgrupo in subgrupos_nome_map.items()
                                if nome in link.lower()
                            ),
                            None,
                        )

                        if subgrupo_nome:
                            categorias_objetos[descricao.lower()] = Categoria(
                                descricao=descricao,
                                link=link,
                                subgrupo=subgrupo_nome,
                            )

            for c in categorias_objetos:
                print(f'categoria: {c}')

            return categorias_objetos, logger.info(
                f'Categorias extraídas com sucesso'
            )

        except Exception as e:
            logger.error(f'Erro ao extrair categorias: {e}')
            return None, logger.error(f'Erro ao extrair categorias: {e}')

    def navigate_to_next_page(self, css_selector):
        """
        Clica no elemento para navegar para a próxima página.

        Args:
            css_selector (str): Seletor CSS do botão para a próxima página.
        """
        self.navigator.find_element_and_click(css_selector)
        logger.info('Navegou para a próxima página com sucesso')

    def _extract_product_info(
        self, produto_element, url, grupo, subgrupo=None, categoria=None
    ):
        """
        Extrai informações de um produto a partir de seu elemento HTML.

        Args:
            produto_element (BeautifulSoup): Elemento contendo as informações do produto.
            url (str): URL da página do produto.
            grupo (str): Nome do grupo.
            subgrupo (str): Nome do subgrupo.
            categoria (str, opcional): Nome da categoria. Default: None.

        Returns:
            Produto: Objeto contendo as informações do produto.
        """
        nome = produto_element.select_one('.product-item__title a')
        preco = produto_element.select_one('.product-item__best-price')

        nome = nome.text.strip() if nome else 'N/A'
        preco_text = preco.text.strip() if preco else '0'
        preco = self._parse_price(preco_text)

        return Produto(
            descricao=nome,
            link=url,
            preco=preco,
            grupo=Grupo(descricao=grupo, link=url),
            subgrupo=Subgrupo(
                descricao=subgrupo,
                link=url,
                grupo=Grupo(descricao=grupo, link=url),
            )
            if subgrupo
            else None,
            categoria=Categoria(
                descricao=categoria,
                link=url,
                subgrupo=Subgrupo(
                    descricao=subgrupo,
                    link=url,
                    grupo=Grupo(descricao=grupo, link=url),
                ),
            )
            if categoria
            else None,
        )

    @staticmethod
    def _parse_price(preco_text):
        """Converte o texto do preço para um número float."""
        try:
            return float(
                preco_text.replace('R$', '')
                .replace('.', '')
                .replace(',', '.')
                .strip()
            )
        except ValueError:
            logger.warning(f'Erro ao converter preço: {preco_text}')
            return 0.0

    def _get_full_url(self, path):
        """Constrói a URL completa a partir de um caminho relativo."""
        return (
            f"{self.url.rstrip('/')}{path}" if path.startswith('/') else path
        )

    def _extract_page_products(self, url, current_path):
        """Extrai todos os produtos de uma página, incluindo a navegação por todas as páginas."""
        produtos = []
        base_url = url.split('#')[0]

        while True:
            try:
                logger.info(f'Acessando link: {url}')
                self.navigator.driver.get(url)
                sleep(5)
                self._wait_for_page_load('body')
                self._scroll_to_bottom()

                soup = BeautifulSoup(
                    self.navigator.driver.page_source, 'html.parser'
                )
                produtos += self._parse_products_on_page(
                    soup, url, current_path
                )
                print(f'Produtos extraídos: {len(produtos)}')

                next_page_button = soup.select_one('.pagination__button--next')
                print(f'next_page_button: {next_page_button}')

                if not next_page_button:
                    logger.info('Botão de próxima página não encontrado')
                    break

                # Verificar se o botão está desabilitado
                if 'pagination__button--disabled' in next_page_button.get(
                    'class', []
                ):
                    logger.info('Botão de próxima página está desabilitado')
                    break

                next_page = next_page_button.get('page')
                if not next_page:
                    logger.info('Atributo page não encontrado no botão')
                    break

                url = f'{base_url}#{next_page}'
                logger.info(f'Navegando para a próxima página: {url}')
                self.navigator.driver.get(url)
                self.navigator.driver.refresh()
                sleep(5)

            except Exception as e:
                logger.error(f'Erro ao extrair produtos: {str(e)}')
                break

        return produtos

    def _parse_products_on_page(self, soup, url, current_path):
        """Extrai produtos de uma página usando BeautifulSoup."""
        product_elements = soup.select('.product-item__info')
        logger.info(
            f'{len(product_elements)} produtos encontrados nesta página'
        )
        for produto_element in product_elements:
            produto = self._extract_product_info(
                produto_element, url, *current_path[:]
            )
            yield produto

    def _wait_for_page_load(self, css_selector):
        """Espera até que o seletor especificado esteja presente na página."""
        WebDriverWait(self.navigator.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def _scroll_to_bottom(self):
        """Rola até o final da página para carregar todos os produtos."""
        self.navigator.driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);'
        )
        sleep(2)

    def scrape_products(self, dicionario):
        """
        Itera sobre os links no dicionário e extrai os produtos.

        Args:
            dicionario (dict): Estrutura contendo os links das páginas de produtos.

        Returns:
            dict: Produtos extraídos por caminho.
        """
        produtos = {}
        self._process_items(dicionario, produtos)
        return produtos

    def _process_items(self, item, produtos, current_path=None):
        """Processa itens do dicionário de forma recursiva."""
        # Garantir que current_path seja uma tupla
        current_path = tuple(current_path or ())

        if url := item.get('link'):
            full_url = self._get_full_url(url)
            logger.info(
                f'Processando URL: {full_url} com caminho {current_path}'
            )
            produtos[current_path] = self._extract_page_products(
                full_url, current_path
            )

        for key, value in item.items():
            if isinstance(value, dict):
                # Adicionar key ao current_path como uma nova tupla
                self._process_items(
                    value, produtos, tuple(current_path) + (key,)
                )

    """scr = Scraper(os.getenv('URL'))
    html = scr.fetch_html()
    scr.navigator.find_element_and_click(
        'pagination__button pagination__button--next'
    )
    if html:
        grupos_objetos = scr.get_grupos(html[0])
        if grupos_objetos:
            subgrupos = scr.get_subgrupos(html[0], grupos_objetos[0])
        if subgrupos:
            categorias = scr.get_categorias(html[0], subgrupos[0])
    """
