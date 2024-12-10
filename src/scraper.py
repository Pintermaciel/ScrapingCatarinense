import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from src.models.categoria import Categoria
from src.models.grupo import Grupo
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
        options.add_argument('--headless=new')
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
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
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
        Navega para a próxima página clicando no elemento com o seletor CSS especificado.

        Args:
            css_selector (str): O seletor CSS do elemento a ser clicado.

        Returns:
            str: Mensagem de confirmação indicando navegação bem-sucedida.

        Raises:
            Exception: Se ocorrer um erro ao navegar para a próxima página.
        """
        self.navigator.find_element_and_click(css_selector)
        return logger.info(f'Navegou para a próxima página com sucesso')


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
