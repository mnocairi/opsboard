from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default="OPEN")