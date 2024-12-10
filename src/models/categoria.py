from pydantic import BaseModel

from src.models.subgrupo import Subgrupo


class Categoria(BaseModel):
    descricao: str
    link: str
    subgrupo: Subgrupo
