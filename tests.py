import os
import json
import pytest
import subprocess
import models

from unittest import mock
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from fastapi.testclient import TestClient

from database import get_db, DB_URL, engine, Base
from main import app
from fetch_municipalities import fetch_municipalities, store_municipalities, main
from populate_kpis import fetch_kpis, populate_kpis

#Setting up test client

client = TestClient(app)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Main.py tests below this line

''' Test read main '''
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

''' Test read municipalities '''
def test_read_municipalities():
    db = next(override_get_db())
    db.query(models.Municipality).filter(models.Municipality.id == "1").all()
    
    response = client.get("/municipalities/")
    assert response.status_code == 200

''' Test read structured municipality data '''
def test_read_structured_municipality_data():
    db = next(override_get_db())   
    response = client.get("/structured_municipality_data/1984?kpi_id=N00003")
    assert response.status_code == 200

# Tests for fetch_municipalities.py

''' Mock fetch_municipalities '''
@pytest.mark.asyncio
async def test_fetch_municipalities():
    mock_response = mock.Mock()
    mock_response.text = '{"values": [{"id": "1", "title": "Test Municipality"}]}'
    
    with mock.patch('httpx.AsyncClient.get', return_value=mock_response):
        data = await fetch_municipalities()
        assert data == '{"values": [{"id": "1", "title": "Test Municipality"}]}'

if __name__ == "__main__":
    subprocess.call(['pytest', '--tb=short', str(__file__)])