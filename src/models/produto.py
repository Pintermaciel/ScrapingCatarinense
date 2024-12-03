from typing import Optional
from pydantic import BaseModel

from models.grupo import Grupo
from models.subgrupo import Subgrupo
from models.categoria import Categoria

class Produto(BaseModel):
    descricao: str
    link: str
    preco: float
    grupo: Grupo
    subgrupo: Subgrupo
    categoria: Optional[Categoria]
    