from pydantic import BaseModel

from src.models.grupo import Grupo


class Subgrupo(BaseModel):
    descricao: str
    link: str
    grupo: Grupo
