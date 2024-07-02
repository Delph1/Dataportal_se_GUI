import asyncio
import httpx
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from typing import List
import json

models.Base.metadata.create_all(bind=engine)

KPI = "N18027"  # Define the KPI as a constant

async def fetch_municipality_data(client: httpx.AsyncClient, municipality_id: str) -> dict:
    url = f"https://api.kolada.se/v2/data/kpi/{KPI}/municipality/{municipality_id}"
    response = await client.get(url)
    return response.json()

async def fetch_all_municipality_data():
    db = SessionLocal()
    try:
        municipalities = db.query(models.Municipality).all()
        async with httpx.AsyncClient() as client:
            for municipality in municipalities:
                print(f"Fetching data for municipality: {municipality.municipality_name}")
                data = await fetch_municipality_data(client, municipality.municipality_id)
                db_item = models.MunicipalityData(
                    municipality_id=municipality.municipality_id,
                    data=json.dumps(data)  # Store the entire response as JSON
                )
                db.add(db_item)
                db.commit()
                print(f"Data stored for municipality: {municipality.municipality_name}")
    finally:
        db.close()

async def main():
    await fetch_all_municipality_data()
    print("All municipality data has been fetched and stored in the database.")

if __name__ == "__main__":
    asyncio.run(main())