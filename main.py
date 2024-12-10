import os

from src.categories import DicionarioAninhador
from src.scraper import Scraper
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    url = os.getenv('URL', 'https://example.com')
    logger.info(f'Starting scraper for URL: {url}')

    dicionario_agrupados = {}

    scraper = Scraper(url)

    html, message = scraper.fetch_html()
    logger.info(message)

    if html:
        grupos_objetos, grupos_message = scraper.get_grupos(html)
        logger.info(grupos_message)

        for grupo in grupos_objetos.values():
            dicionario_agrupados[grupo.descricao.lower()] = {
                'grupo': grupo.descricao,
                'link': grupo.link,
            }

        if grupos_objetos:
            subgrupos, subgrupos_message = scraper.get_subgrupos(html, grupos_objetos)
            logger.info(subgrupos_message)

            for subgrupo in subgrupos.values():
                dicionario_agrupados[subgrupo.descricao.lower()] = {
                    'subgrupo': subgrupo.descricao,
                    'link': subgrupo.link,
                    'grupo': subgrupo.grupo.descricao,
                }

            if subgrupos:
                categorias, categorias_message = scraper.get_categorias(html, subgrupos)
                logger.info(categorias_message)

                for categoria in categorias.values():
                    dicionario_agrupados[categoria.descricao.lower()] = {
                        'categoria': categoria.descricao,
                        'link': categoria.link,
                        'subgrupo': categoria.subgrupo.descricao,
                        'grupo': categoria.subgrupo.grupo.descricao,
                    }

                simplificador = DicionarioAninhador(dicionario_agrupados)
                simplificador.aninhar()

                logger.info(f"Resultado final do aninhamento: {simplificador.obter_dicionario()}")


if __name__ == '__main__':
    main()
