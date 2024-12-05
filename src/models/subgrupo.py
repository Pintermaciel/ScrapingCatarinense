from pydantic import BaseModel

from models.grupo import Grupo

class Subgrupo(BaseModel):
    descricao: str
    link: str
    grupo: Grupo 