import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

from models.grupo import Grupo
from utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv()

class Scraper:
    def __init__(self, url):
        self.url = url
        self.css_grupos = os.getenv('CSS_GRUPOS')

    def fetch_html(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            logger.info(
                f"""HTML fetched successfully 
                {response.status_code}"""
                )
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching HTML: {e}")
            return None
        
    def get_grupos(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            grupos = soup.select('li[data-menu]')

            grupos_objetos = []

            for grupo in grupos:
                try:
                    tag_a = grupo.find('a')
                    if tag_a:
                        descricao = tag_a.get_text(strip=True)
                        link = tag_a['href']  
                        grupos_objetos.append(
                            Grupo(
                                descricao=descricao,
                                link=link
                            )
                        )
                except KeyError as e:
                    logger.error(f"Erro ao processar grupo: {e}")
                except Exception as e:
                    logger.error(f"Erro inesperado: {e}")
            for g in grupos_objetos:
                print(g)
        except Exception as e:
            logger.error(f"Erro ao extrair grupos: {e}")
            return None
    
scr = Scraper(os.getenv('URL'))
html = scr.fetch_html()
grupos = scr.get_grupos(html)