from pydantic import BaseModel
class Grupo(BaseModel):
    descricao: str
    link: str