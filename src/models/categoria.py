from pydantic import BaseModel

from models.grupo import Grupo
from models.produto import Produto
from models.subgrupo import Subgrupo

class Categoria(BaseModel):
    descricao: str
    link: str
    grupo: Grupo
    subgrupo: Subgrupo
    produtos: list[Produto] = []