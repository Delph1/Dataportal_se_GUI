from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))

class Municipality(Base):
    __tablename__ = "municipalities"

    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(String(10), unique=True, index=True)
    municipality_name = Column(String(100))
    data = relationship("MunicipalityData", back_populates="municipality")

class MunicipalityData(Base):
    __tablename__ = "municipality_data"

    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(String(10), ForeignKey("municipalities.municipality_id"))
    data = Column(JSON)  # Store all data as JSON
    municipality = relationship("Municipality", back_populates="data")