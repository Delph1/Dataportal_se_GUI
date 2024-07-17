import models
import httpx
import json
import logging
import schemas

from database import engine, get_db
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fetch_municipality_data import fetch_single_municipality_data
from sqlalchemy.orm import Session
from typing import List

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='app.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

''' Main page '''
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

''' Gets a list of municipalities from the database '''
@app.get("/municipalities/", response_model=List[schemas.Municipality])
def read_municipalities(db: Session = Depends(get_db)):
    return db.query(models.Municipality).all()

''' Node to view the data "as is" for a specific municipality and KPI '''
@app.get("/municipality_data/{municipality_id}", response_model=schemas.MunicipalityData)
def read_municipality_data(municipality_id: str, kpi_id: int = 1, db: Session = Depends(get_db)):
    data = db.query(models.MunicipalityData).filter(
        models.MunicipalityData.municipality_id == municipality_id,
        models.MunicipalityData.kpi_id == kpi_id
    ).all()
    if not data:
        raise HTTPException(status_code=404, detail="Municipality data not found")
    
    # Parse the JSON string back into a Python object
    data.data = json.loads(data.data)
    
    return data

''' Gets the data for a specific municipality and KPI from the database '''
@app.get("/structured_municipality_data/{municipality_id}", response_model=schemas.StructuredMunicipalityData)
def read_structured_municipality_data(municipality_id: str, kpi_id: str, db: Session = Depends(get_db)):
    try:
        municipality = db.query(models.Municipality).filter(models.Municipality.municipality_id == municipality_id).first()
        if not municipality:
            logger.error(f"Municipality not found: {municipality_id}")
            raise HTTPException(status_code=404, detail="Municipality not found")

        kpi = db.query(models.KPI).filter(models.KPI.kpi_id == kpi_id).first()
        if not kpi:
            logger.error(f"KPI not found: {kpi_id}")
            raise HTTPException(status_code=404, detail="KPI not found")

        municipality_data = db.query(models.MunicipalityData).filter(
            models.MunicipalityData.municipality_id == municipality_id,
            models.MunicipalityData.kpi_id == kpi_id).all()
        
        data = [
            {
                "value": json.loads(data.data)
            }
            for data in municipality_data
        ]
        return schemas.StructuredMunicipalityData(
            municipality_id=municipality.municipality_id,
            municipality_name=municipality.municipality_name,
            kpi_id=kpi.id,
            kpi_name=kpi.name,
            auspices=kpi.auspices,
            has_ou_data=kpi.has_ou_data,
            is_divided_by_gender=kpi.is_divided_by_gender,
            municipality_type=kpi.municipality_type,
            operating_area=kpi.operating_area,
            ou_publication_date=kpi.ou_publication_date,
            perspective=kpi.perspective,
            prel_publication_date=kpi.prel_publication_date,
            publ_period=kpi.publ_period,
            publication_date=kpi.publication_date,
            values=data
        )
    except Exception as e:
        logger.exception(f"Error processing data for municipality {municipality_id}")
        raise HTTPException(status_code=500, detail=str(e))
    
''' Downloads data from the dataportal.se API a.k.a. kolada.se '''
@app.get("/fetch_municipality_data")
async def fetch_municipality_data(kpi_id: str, municipality_id: str, db: Session = Depends(get_db)):
    try:
        exists = data_exists_in_database(db, kpi_id, municipality_id)   
        if exists == False:
            print(f"Fetching data for KPI: {kpi_id}, Municipality: {municipality_id}")
            async with httpx.AsyncClient() as client:
                response =  await client.get(f"https://api.kolada.se/v2/data/kpi/{kpi_id}/municipality/{municipality_id}")
                data = response.json()
                db_item = models.MunicipalityData(
                    municipality_id=municipality_id,
                    kpi_id=kpi_id,
                    data=json.dumps(data)
                )
                db.add(db_item)
                db.commit()
            return response.json()
        else:
            print(f"Data already exists for KPI: {kpi_id}, Municipality: {municipality_id}")
    except Exception as e:
        db.rollback()
        print(f"Error fetching and saving municipality data: {e}")
    finally:
        db.close()

''' Simple function to check if a datapost already exists so we don't need to download it again '''
def data_exists_in_database(db: Session, kpi_id: str, municipality_id: str) -> bool:
    existing_data = db.query(models.MunicipalityData) \
                      .filter(models.MunicipalityData.kpi_id == kpi_id,
                              models.MunicipalityData.municipality_id == municipality_id) \
                      .first()
    print(existing_data)
    if existing_data is None:
        return False
    else:
        return True

''' Gets a list of KPIs and their metadata from the database '''
@app.get("/kpis/", response_model=List[schemas.KPI])
def read_kpis(db: Session = Depends(get_db)):
    try:
        logger.info("Fetching KPIs from the database")
        kpis = db.query(models.KPI).all()
        logger.info(f"Retrieved {len(kpis)} KPIs")
        return kpis
    except Exception as e:
        logger.error("Error fetching KPIs:", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching KPIs")

''' users currently not implemented '''
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

