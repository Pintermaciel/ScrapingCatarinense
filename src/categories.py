import logging


def get_logger(name: str) -> logging.Logger:
    """Configuração de log simples."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(name)
    return logger


class DicionarioAninhador:
    """
    Classe responsável por aninhar os dados corretamente nos níveis hierárquicos:
    1. Grupo
    2. Subgrupo
    3. Categoria (opcional)
    """

    def __init__(self, dicionario):
        """
        Inicializa com o dicionário que será processado.
        Args:
            dicionario (dict): O dicionário já tratado pela lógica anterior.
        """
        self.dicionario = dicionario
        self.logger = get_logger(__name__)
        self.logger.info("Iniciando estrutura do aninhador com múltiplos níveis.")

    def aninhar(self):
        """
        Função principal para realizar o aninhamento hierárquico com ou sem 'categoria'.
        Estrutura esperada:
        - Grupo -> Subgrupo
        - Se existir Categoria, armazene neste nível
        """
        try:
            self.logger.info("Processando para aninhamento...")
            novo_dicionario = {}

            # Iterar sobre todos os itens e reorganizar em níveis
            for key, value in self.dicionario.items():
                grupo = value.get("grupo")
                subgrupo = value.get("subgrupo")
                categoria = value.get("categoria")
                link = value.get("link", "")

                # Se o grupo existir, criar ou adicionar estrutura
                if grupo:
                    if grupo not in novo_dicionario:
                        novo_dicionario[grupo] = {}

                    # Se o subgrupo existir, criar ou adicionar estrutura
                    if subgrupo:
                        if subgrupo not in novo_dicionario[grupo]:
                            novo_dicionario[grupo][subgrupo] = {}

                        # Caso exista uma categoria, armazenar neste nível
                        if categoria:
                            novo_dicionario[grupo][subgrupo][categoria] = {
                                "link": link,
                                "grupo": grupo,
                                "subgrupo": subgrupo,
                                "categoria": categoria,
                            }
                        else:  # Caso não exista a categoria, armazenar apenas no subgrupo
                            novo_dicionario[grupo][subgrupo] = {
                                "link": link,
                                "grupo": grupo,
                                "subgrupo": subgrupo,
                            }
                    else:
                        novo_dicionario[grupo] = {
                            "link": link,
                        }

            self.dicionario = novo_dicionario
            self.logger.info("Aninhamento concluído com sucesso!")
        except Exception as e:
            self.logger.error(f"Erro ao aninhar o dicionário: {e}")

    def obter_dicionario(self):
        """
        Retorna o dicionário aninhado após o processo.
        """
        return self.dicionario
