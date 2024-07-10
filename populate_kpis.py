from database import SessionLocal, engine
import models
import httpx
import asyncio

models.Base.metadata.create_all(bind=engine)

async def fetch_kpis():
    kpi_data = []
    for url in ["https://api.kolada.se/v2/kpi", "https://api.kolada.se/v2/kpi?page=2&per_page=5000"]:
        print(f"Fetching data from: {url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        data = response.json()
        kpi_data.extend(data['values'])
    print(f"Total KPIs fetched: {len(kpi_data)}")
    return kpi_data

def populate_kpis(kpi_data: str):
    db = SessionLocal()
    try:
        # Check if any KPIs already exist
        kpi_count = db.query(models.KPI).count()
        if kpi_count > 0:
            print("KPIs already exist in the database. Skipping population.")
            return

        # Add the KPIs to the database
        for kpi_to_add in kpi_data:
            db_kpi = models.KPI(
                kpi_id=kpi_to_add["id"],
                name=kpi_to_add["title"],
                description=kpi_to_add["description"],
                auspices=kpi_to_add["auspices"],
                has_ou_data=kpi_to_add["has_ou_data"],
                is_divided_by_gender=kpi_to_add["is_divided_by_gender"],
                municipality_type=kpi_to_add["municipality_type"],
                operating_area=kpi_to_add["operating_area"],
                ou_publication_date=kpi_to_add["ou_publication_date"],
                perspective=kpi_to_add["perspective"],
                prel_publication_date=kpi_to_add["prel_publication_date"],
                publ_period=kpi_to_add["publ_period"],
                publication_date=kpi_to_add["publication_date"]
            )
                            
            db.add(db_kpi)
        db.commit()
        print("KPIs populated successfully.")
    except Exception as e:
        print("Error populating KPIs:", e)
    finally:
        print("Done")
        db.close()

async def main():
    kpi_data = await fetch_kpis()
    populate_kpis(kpi_data)
    print("KPIs has been fetched and stored in the database.")

if __name__ == "__main__":
    asyncio.run(main())