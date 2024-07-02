from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas
import httpx
from typing import List
import json
import logging

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/municipalities/", response_model=List[schemas.Municipality])
def read_municipalities(db: Session = Depends(get_db)):
    return db.query(models.Municipality).all()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(username=user.username, email=user.email, hashed_password=user.password) 
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/fetch-kolada-data")
async def fetch_kolada_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.kolada.se/v2/kpi/N18027")
    return response.json()

@app.get("/municipality_data/{municipality_id}", response_model=schemas.MunicipalityData)
def read_municipality_data(municipality_id: str, db: Session = Depends(get_db)):
    data = db.query(models.MunicipalityData).filter(
        models.MunicipalityData.municipality_id == municipality_id
    ).first()
    if not data:
        raise HTTPException(status_code=404, detail="Municipality data not found")
    
    # Parse the JSON string back into a Python object
    data.data = json.loads(data.data)
    
    return data

@app.get("/structured_municipality_data/{municipality_id}", response_model=schemas.StructuredMunicipalityData)
def read_structured_municipality_data(municipality_id: str, db: Session = Depends(get_db)):
    try:
        municipality = db.query(models.Municipality).filter(models.Municipality.municipality_id == municipality_id).first()
        if not municipality:
            logger.error(f"Municipality not found: {municipality_id}")
            raise HTTPException(status_code=404, detail="Municipality not found")

        data = db.query(models.MunicipalityData).filter(
            models.MunicipalityData.municipality_id == municipality_id
        ).first()
        if not data:
            logger.error(f"Municipality data not found: {municipality_id}")
            raise HTTPException(status_code=404, detail="Municipality data not found")
        
        json_data = json.loads(data.data)
        logger.info(f"JSON data for {municipality_id}: {json_data}")
        
        kpi_values = []
        for value in json_data.get('values', []):
            value_data = value.get('values', [{}])[0]
            if isinstance(value_data, dict):
                actual_value = value_data.get('value')
                metadata = {k: v for k, v in value_data.items() if k != 'value'}
            else:
                actual_value = value_data
                metadata = {}

            kpi_values.append(schemas.KpiValue(
                kpi=value.get('kpi'),
                year=value.get('period'),
                value=actual_value,
                metadata=metadata
            ))

        return schemas.StructuredMunicipalityData(
            municipality_id=municipality.municipality_id,
            municipality_name=municipality.municipality_name,
            values=kpi_values
        )
    except Exception as e:
        logger.exception(f"Error processing data for municipality {municipality_id}")
        raise HTTPException(status_code=500, detail=str(e))