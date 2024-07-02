import httpx
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import asyncio
import json

models.Base.metadata.create_all(bind=engine)

async def fetch_municipalities():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.kolada.se/v2/municipality")
        return response.text  # Return raw text instead of parsed JSON

def store_municipalities(data: str):
    db = SessionLocal()
    try:
        print("Raw data received:")
        print(data[:1000])  # Print first 1000 characters of raw data
        
        json_data = json.loads(data)
        print("JSON data structure:")
        print(json.dumps(json_data, indent=2)[:1000])  # Print first 1000 characters of formatted JSON
        
        if 'values' not in json_data:
            print("Error: 'values' key not found in data")
            print("Available keys:", json_data.keys())
            return
        
        for municipality in json_data['values']:
            print(f"Processing municipality: {municipality}")
            municipality_id = municipality.get('id')
            municipality_name = municipality.get('title')
            
            if municipality_id and municipality_name:
                db_municipality = models.Municipality(
                    municipality_id=municipality_id,
                    municipality_name=municipality_name
                )
                db.add(db_municipality)
            else:
                print(f"Skipping municipality due to missing data: {municipality}")
        
        db.commit()
        print(f"Stored {len(json_data['values'])} municipalities")
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print("Raw data causing the error:")
        print(data)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

async def main():
    data = await fetch_municipalities()
    store_municipalities(data)
    print("Municipalities data has been fetched and stored in the database.")

if __name__ == "__main__":
    asyncio.run(main())