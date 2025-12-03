import os
import pytest

os.environ["SQLITE_DATABASE_LOCATION"] = "../db/tests.db"
os.environ["SQL_SETUP"] = "../db/schema.sql"
os.environ["DEPLOYMENT_ENV"] = "test"

from app.app import app, init_db_core, db_connection

def insert_test_vehicle(
    vin="TESTVIN-123",
    manufacturer_name="TestMaker",
    description="Test Description",
    horse_power=150,
    model_name="TestModel",
    model_year=2024,
    purchase_price=25000.00,
    fuel_type="Gasoline",
):
    """
    Purpose:
        Helper function used to insert a dummy record for Unit Testing Purposes
    """
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO vehicles (
            vin, manufacturer_name, description, horse_power,
            model_name, model_year, purchase_price, fuel_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            vin,
            manufacturer_name,
            description,
            horse_power,
            model_name,
            model_year,
            purchase_price,
            fuel_type,
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return vin



@pytest.fixture(scope="function")
def client():
    """
    Purpose:
        This client function will create a fresh Flask client with a cleaned database for each test
    """
    init_db_core()

    with app.test_client() as client:
        yield client


def test_get_vehicles_empty(client):
    """
    GET /vehicle on a fresh DB should return 200 and an empty list.
    """
    response = client.get("/vehicle")
    assert response.status_code == 200

    data = response.get_json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 0


def test_get_vehicles_with_data(client):
    """
    GET /vehicle should return the vehicles that exist in the DB.
    """
    vin1 = insert_test_vehicle(vin="VIN-1", manufacturer_name="Honda")
    vin2 = insert_test_vehicle(vin="VIN-2", manufacturer_name="Toyota")

    response = client.get("/vehicle")
    assert response.status_code == 200

    data = response.get_json()
    vehicles = data["data"]
    vins = {v["vin"] for v in vehicles}

    assert vin1 in vins
    assert vin2 in vins


def test_create_vehicle_success(client):
    """
    POST /vehicle should create a new vehicle and return 201,
    with the created record (including generated vin).
    """
    payload = {
        "manufacturer_name": "Honda",
        "description": "Sedan",
        "horse_power": 140,
        "model_name": "Civic",
        "model_year": 2020,
        "purchase_price": 20000.0,
        "fuel_type": "Gasoline",
    }

    response = client.post("/vehicle", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert "data" in data
    created = data["data"]

    assert created["manufacturer_name"] == "Honda"
    assert created["model_name"] == "Civic"
    assert created["model_year"] == 2020
    assert "vin" in created
    assert isinstance(created["vin"], str)

    # Confirm it appears in GET /vehicle
    list_response = client.get("/vehicle")
    assert list_response.status_code == 200
    list_data = list_response.get_json()
    vins = [v["vin"] for v in list_data["data"]]
    assert created["vin"] in vins


def test_create_vehicle_non_json_body(client):
    """
    POST /vehicle with non-JSON body should return 400.
    """
    response = client.post(
        "/vehicle",
        data="not json at all",
        content_type="text/plain",
    )
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Request does not use a JSON format"


def test_create_vehicle_missing_field(client):
    payload = {
        "manufacturer_name": "Honda",
        "description": "Sedan",
        "horse_power": 140,
        "model_name": "Civic",
        "model_year": 2020,
        "purchase_price": 20000.0,
    }

    response = client.post("/vehicle", json=payload)
    assert response.status_code == 422

    data = response.get_json()
    assert "error" in data


def test_create_vehicle_extra_field(client):
    """
    POST /vehicle with an unexpected extra field should return 422.
    """
    payload = {
        "manufacturer_name": "Honda",
        "description": "Sedan",
        "horse_power": 140,
        "model_name": "Civic",
        "model_year": 2020,
        "purchase_price": 20000.0,
        "fuel_type": "Gasoline",
        "color": "Blue",
    }

    response = client.post("/vehicle", json=payload)
    assert response.status_code == 422

    data = response.get_json()
    assert "error" in data


def test_create_vehicle_wrong_type(client):
    '''
    Purpose
    '''
    payload = {
        "manufacturer_name": "Honda",
        "description": "Sedan",
        "horse_power": "140",
        "model_name": "Civic",
        "model_year": 2020,
        "purchase_price": 20000.0,
        "fuel_type": "Gasoline",
    }

    response = client.post("/vehicle", json=payload)
    assert response.status_code == 422

    data = response.get_json()
    assert "error" in data


def test_get_vehicle_by_vin_found(client):
    vin = insert_test_vehicle()

    response = client.get(f"/vehicle/{vin}")
    assert response.status_code == 200

    data = response.get_json()
    assert "data" in data
    vehicles = data["data"]
    assert len(vehicles) == 1

    vehicle = vehicles[0]
    assert vehicle["vin"] == vin


def test_get_vehicle_by_vin_not_found(client):
    response = client.get("/vehicle/NON_EXISTENT_VIN")
    assert response.status_code == 404

    data = response.get_json()
    assert "error" in data


def test_update_vehicle_success(client):
    """
    PUT /vehicle/<vin> should update an existing vehicle and return 200.
    """
    vin = insert_test_vehicle()

    update_payload = {
        "manufacturer_name": "FordUpdated",
        "description": "Updated description",
        "horse_power": 180,
        "model_name": "FocusUpdated",
        "model_year": 2021,
        "purchase_price": 21000.0,
        "fuel_type": "Gasoline",
    }

    response = client.put(f"/vehicle/{vin}", json=update_payload)
    assert response.status_code == 200

    data = response.get_json()
    updated = data["data"]

    assert updated["vin"] == vin


def test_update_vehicle_non_json_body(client):
    """
    PUT /vehicle/<vin> with non-JSON body should return 400.
    """
    vin = insert_test_vehicle(vin="VIN-UPDATE-NOJSON")

    response = client.put(
        f"/vehicle/{vin}",
        data="not json",
        content_type="text/plain",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_update_vehicle_invalid_payload(client):
    """
    PUT /vehicle/<vin> with invalid payload (missing fields / wrong types)
    should return 422.
    """
    vin = insert_test_vehicle(vin="VIN-UPDATE-BADPAYLOAD")

    payload = {
        "description": "Only description provided",
    }

    response = client.put(f"/vehicle/{vin}", json=payload)
    assert response.status_code == 422

    data = response.get_json()
    assert "error" in data


def test_update_vehicle_not_found(client):
    """
    PUT /vehicle/<vin> for a non-existent vin should return 422,
    as per current implementation.
    """
    payload = {
        "manufacturer_name": "NoCar",
        "description": "Does not exist",
        "horse_power": 100,
        "model_name": "Ghost",
        "model_year": 1999,
        "purchase_price": 1.0,
        "fuel_type": "Ectoplasm",
    }

    response = client.put("/vehicle/NON_EXISTENT_VIN", json=payload)
    assert response.status_code == 422

    data = response.get_json()
    assert "error" in data
    assert "does not exist" in data["error"]


def test_delete_vehicle_success(client):
    """
    DELETE /vehicle/<vin> should return 204 and actually remove the vehicle.
    """
    vin = insert_test_vehicle()

    response = client.delete(f"/vehicle/{vin}")
    assert response.status_code == 204

    get_response = client.get(f"/vehicle/{vin}")
    assert get_response.status_code == 404


def test_delete_vehicle_not_found(client):
    response = client.delete("/vehicle/NON_EXISTENT_VIN")
    assert response.status_code == 404

    data = response.get_json()
    assert "error" in data
