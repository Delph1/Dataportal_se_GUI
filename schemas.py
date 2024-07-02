from pydantic import BaseModel
from typing import List, Optional, Any

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
    data: Any  # This will contain the entire JSON data

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
    kpi: str
    year: int
    value: Optional[float]
    metadata: Optional[dict]  


class StructuredMunicipalityData(BaseModel):
    municipality_id: str
    municipality_name: str
    values: List[KpiValue]