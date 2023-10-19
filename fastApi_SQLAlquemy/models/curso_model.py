from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.config import settings


class CursoModel(settings.DBBaseModel):
    __tablename__ = "cursos"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    titulo: str = Column(String(100))
    aulas: int = Column(Integer)
    horas: int = Column(Integer)
    alunos = relationship("AlunosModel")
