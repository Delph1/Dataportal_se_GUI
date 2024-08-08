from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))

class Municipality(Base):
    __tablename__ = "municipalities"

    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(String(10), unique=True, index=True)
    municipality_name = Column(String(100))
    data = relationship("MunicipalityData", back_populates="municipality")

class KPI(Base):
    __tablename__ = "kpis"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    kpi_id = Column(String(10), unique=True, index=True)
    name = Column(String(255))
    description = Column(TEXT)
    auspices = Column(String(255))
    has_ou_data = Column(Boolean)
    is_divided_by_gender = Column(Integer)
    municipality_type = Column(String(255))
    operating_area = Column(String(255))
    ou_publication_date = Column(String(50))
    perspective = Column(String(50))
    prel_publication_date = Column(String(50))
    publ_period = Column(String(50))
    publication_date = Column(String(50))

class MunicipalityData(Base):
    __tablename__ = "municipality_data"

    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(String(10), ForeignKey("municipalities.municipality_id"))
    data = Column(JSON)  # Store all data as JSON
    kpi_id = Column(String(10), ForeignKey("kpis.kpi_id"))
    municipality = relationship("Municipality", back_populates="data")
