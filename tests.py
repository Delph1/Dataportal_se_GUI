import pytest
import subprocess

from unittest import mock
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from main import app, get_db
from fetch_municipalities import fetch_municipalities

#Setting up test client

client = TestClient(app)

# SQLAlchemy setup for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency override
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