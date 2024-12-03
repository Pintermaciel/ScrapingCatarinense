from pydantic import BaseModel

from models.grupo import Grupo
from models.produto import Produto

class Subgrupo(BaseModel):
    descricao: str
    link: str
    grupo: Grupo
    produtos: list[Produto] = []