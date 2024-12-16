from typing import Optional

from pydantic import BaseModel

from src.models.categoria import Categoria
from src.models.grupo import Grupo
from src.models.subgrupo import Subgrupo


class Produto(BaseModel):
    descricao: str
    link: str
    preco: float
    grupo: Grupo
    subgrupo: Optional[Subgrupo]
    categoria: Optional[Categoria]
