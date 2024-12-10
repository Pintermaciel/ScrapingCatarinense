import logging


def get_logger(name):
    """
    Inicializa um logger com o nome especificado.

    Args:
        name (str): O nome do logger.

    Returns:
        logging.Logger: Um objeto Logger configurado.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
