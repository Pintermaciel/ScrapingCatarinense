import logging


def get_logger(name: str) -> logging.Logger:
    """
    Configura e retorna um logger personalizado.

    Args:
        name (str): Nome do logger a ser criado.

    Returns:
        logging.Logger: Logger configurado com nível INFO.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger(name)
    return logger


class DicionarioAninhador:
    """
    Classe responsável por organizar dados em uma estrutura hierárquica aninhada.

    A hierarquia é organizada em três níveis:
    1. Grupo (nível superior)
    2. Subgrupo (nível intermediário)
    3. Categoria (nível opcional inferior)

    Attributes:
        dicionario (dict): Dicionário contendo os dados a serem aninhados.
        logger (logging.Logger): Logger para registro de operações.
    """

    def __init__(self, dicionario: dict):
        """
        Inicializa o aninhador com o dicionário a ser processado.

        Args:
            dicionario (dict): Dicionário contendo dados já tratados pela lógica anterior.
            Deve conter chaves como 'grupo', 'subgrupo' e opcionalmente 'categoria'.
        """
        self.dicionario = dicionario
        self.logger = get_logger(__name__)
        self.logger.info(
            'Iniciando estrutura do aninhador com múltiplos níveis.'
        )

    def aninhar(self) -> dict:
        """
        Realiza o aninhamento hierárquico dos dados.

        A estrutura resultante terá o formato:
        {
            "grupo1": {
                "subgrupo1": {
                    "categoria1": {
                        "link": "url",
                        "grupo": "grupo1",
                        "subgrupo": "subgrupo1",
                        "categoria": "categoria1"
                    }
                }
            }
        }

        Returns:
            dict: Novo dicionário com a estrutura aninhada.

        Raises:
            Exception: Caso ocorra algum erro durante o processo de aninhamento.
        """
        try:
            self.logger.info('Processando para aninhamento...')
            novo_dicionario = {}

            for key, value in self.dicionario.items():
                grupo = value.get('grupo')
                subgrupo = value.get('subgrupo')
                categoria = value.get('categoria')
                link = value.get('link', '')

                if grupo:
                    if grupo not in novo_dicionario:
                        novo_dicionario[grupo] = {}

                    if subgrupo:
                        if subgrupo not in novo_dicionario[grupo]:
                            novo_dicionario[grupo][subgrupo] = {}

                        if categoria:
                            novo_dicionario[grupo][subgrupo][categoria] = {
                                'link': link,
                                'grupo': grupo,
                                'subgrupo': subgrupo,
                                'categoria': categoria,
                            }
                        else:
                            novo_dicionario[grupo][subgrupo] = {
                                'link': link,
                                'grupo': grupo,
                                'subgrupo': subgrupo,
                            }
                    else:
                        novo_dicionario[grupo] = {
                            'link': link,
                        }

            self.dicionario = novo_dicionario
            self.logger.info('Aninhamento concluído com sucesso!')
            return novo_dicionario
        except Exception as e:
            self.logger.error(f'Erro ao aninhar o dicionário: {e}')

    def obter_dicionario(self) -> dict:
        """
        Retorna o dicionário após o processo de aninhamento.

        Returns:
            dict: Dicionário com a estrutura hierárquica aninhada.
        """
        return self.dicionario
