from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
from models.categoria import Categoria
from models.grupo import Grupo
from models.subgrupo import Subgrupo
from utils.logger import get_logger

logger = get_logger(__name__)

class Scraper:
    def __init__(self, url):
        self.url = url
        self.css_grupos = os.getenv('CSS_GRUPOS')

    def fetch_html(self):
        try:
            options = webdriver.ChromeOptions()
            options.headless = False
            driver = webdriver.Chrome(
                service=Service(
                    ChromeDriverManager().install()
                    ),
                options=options
                )

            driver.get(self.url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        self.css_grupos
                        )
                    )
            )

            html = driver.page_source
            driver.quit()

            logger.info("HTML fetched successfully")
            return html
        except Exception as e:
            logger.error(
                f"Error fetching HTML with Selenium: {e}"
                )
            return None

    def get_grupos(self, html):
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
                            descricao=descricao,
                            link=link
                        )
                except KeyError as e:
                    logger.error(
                        f"Erro ao processar grupo: {e}"
                        )
                except Exception as e:
                    logger.error(
                        f"""Erro inesperado ao processar grupo:
                        {e}"""
                        )

            for g in grupos_objetos:
                print(f"grupo: {g}")

            return grupos_objetos
        except Exception as e:
            logger.error(f"Erro ao extrair grupos: {e}")
            return None

    def get_subgrupos(self, html, grupos_objetos):
        try:
            soup = BeautifulSoup(html, 'html.parser')

            subgrupos_objetos = {}

            grupos_nome_map = {
                grupo.descricao.lower(): grupo 
                for grupo in grupos_objetos.values()
            }

            for subgrupo in soup.select(
                'div.submenu.submenu--level-2'
                ):
                for li in subgrupo.find_all(
                        'li', 
                        class_='submenu__item submenu__item--main'):
                    tag_a = li.find('a')
                    if tag_a:
                        descricao = tag_a.get_text(strip=True)
                        link = tag_a['href']

                        grupo_nome = next(
                            (
                                grupo for nome, grupo in grupos_nome_map.items() 
                                if nome in link.lower()
                            ), 
                            None
                        )

                        if grupo_nome:
                            subgrupos_objetos[descricao.lower()] = Subgrupo(
                                    descricao=descricao,
                                    link=link,
                                    grupo=grupo_nome
                                )

            for s in subgrupos_objetos:
                print(f"subgrupo: {s}")
            return subgrupos_objetos

        except Exception as e:
            logger.error(f"Erro ao extrair subgrupos: {e}")
            return None

    def get_categorias(self, html, subgrupos_objetos):
        try:
            soup = BeautifulSoup(html, 'html.parser')

            categorias_objetos = {}

            subgrupos_nome_map = {
                subgrupo.descricao.lower(): subgrupo
                for subgrupo in subgrupos_objetos.values()
            }

            for categoria in soup.select(
                'div.submenu.submenu--level-3'
                ):
                for li in categoria.find_all(
                    'li', 
                    class_='submenu__item'
                ):
                    tag_a = li.find('a')
                    if tag_a:
                        descricao = tag_a.get_text(strip=True)
                        link = tag_a.get('href')

                        # Procurar o subgrupo correspondente
                        subgrupo_nome = next(
                            (
                                subgrupo for nome, subgrupo in subgrupos_nome_map.items()
                                if nome in link.lower()
                            ),
                            None
                        )

                        if subgrupo_nome:
                            categorias_objetos[descricao.lower()] = Categoria(
                                descricao=descricao,
                                link=link,
                                subgrupo=subgrupo_nome
                            )

            for c in categorias_objetos:
                print(f"categoria: {c}")

            return categorias_objetos

        except Exception as e:
            logger.error(f"Erro ao extrair categorias: {e}")
            return None


scr = Scraper(os.getenv('URL'))
html = scr.fetch_html()
if html:
    grupos_objetos = scr.get_grupos(html)
    if grupos_objetos:
        subgrupos = scr.get_subgrupos(html, grupos_objetos)
    if subgrupos:
        categorias = scr.get_categorias(html, subgrupos)
    
