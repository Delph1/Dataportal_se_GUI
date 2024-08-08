import pytest
import subprocess

from unittest import mock
from fastapi.testclient import TestClient

from main import app
from fetch_municipalities import fetch_municipalities

#Setting up test client

client = TestClient(app)

# Main.py tests below this line

''' Test read main '''
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

''' Test read municipalities '''
def test_read_municipalities():
    
    response = client.get("/municipalities/")
    assert response.status_code == 200

''' Test read structured municipality data '''
def test_read_structured_municipality_data():
    response = client.get("/structured_municipality_data/1984?kpi_id=N00003")
    assert response.status_code == 200


if __name__ == "__main__":
    subprocess.call(['pytest', '--tb=short', str(__file__)])