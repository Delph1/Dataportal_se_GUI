from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class KPI(BaseModel):
    id: int
    kpi_id: str
    name: str
    description: str
    auspices: Optional[str] = Field(default=None)
    has_ou_data: Optional[bool] = Field(default=None)
    is_divided_by_gender: int
    municipality_type: str
    operating_area: Optional[str] = Field(default=None)
    ou_publication_date: Optional[str]
    perspective: Optional[str] = Field(default=None)
    prel_publication_date: Optional[str]
    publ_period: Optional[str]
    publication_date: Optional[str]

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class MunicipalityBase(BaseModel):
    municipality_id: str
    municipality_name: str

class Municipality(MunicipalityBase):
    id: int

    class Config:
        from_attributes = True

class MunicipalityDataBase(BaseModel):
    municipality_id: str
    kpi_id: int
    data: str

class MunicipalityDataCreate(MunicipalityDataBase):
    pass

class MunicipalityData(MunicipalityDataBase):
    id: int
    

    class Config:
        from_attributes = True

class MunicipalityWithData(Municipality):
    data: List[MunicipalityData] = []

    class Config:
        from_attributes = True

# Additional schemas for structured data access
class KpiValue(BaseModel):
    value: Optional[dict]

class StructuredMunicipalityData(BaseModel):
    municipality_id: str
    municipality_name: str
    kpi_id: int
    kpi_name: str
    values: List[KpiValue]