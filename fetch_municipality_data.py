import asyncio
import httpx
from database import SessionLocal, engine
import models
import json

models.Base.metadata.create_all(bind=engine)

async def fetch_single_municipality_data(client: httpx.AsyncClient, kpi_id: str, municipality_id: str) -> dict:
    url = f"https://api.kolada.se/v2/data/kpi/{kpi_id}/municipality/{municipality_id}"
    response = await client.get(url)
    return response.json()

async def fetch_all_municipality_data(kpi_id: str, municipality_ids: str):
    db = SessionLocal()
    try:
        # Fetch all municipalities for the given KPI
        municipalities = municipality_ids
        async with httpx.AsyncClient() as client:
            for municipality in municipalities:
                print(f"Fetching data for KPI: {kpi_id}, Municipality: {municipality}")
                data = await fetch_single_municipality_data(client, kpi_id, municipality)
                db_item = models.MunicipalityData(
                    municipality_id=municipality,
                    kpi_id=kpi_id,
                    year=data["year"],
                    value=data["value"],
                    data=json.dumps(data)
                )
                db.add(db_item)
                db.commit()
                print(f"Data stored for KPI: {kpi_id}, Municipality: {municipality}")
    except Exception as e:
        db.rollback()
        print(f"Error fetching and saving municipality data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(fetch_all_municipality_data("N18027"))  # Example KPI ID