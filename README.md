# VehicleAPIApollo
This project provides an overview of the Vehicle CRUD service built for the Apollo Global Management interview process.
---

# Requirements
To run this project, ensure you have the following installed:
- **Homebrew (brew)**  
- **Python 3**
---

# Project Setup

## Setup Python Environment
1. In the root folder, create a virtual environment
```bash
python3 -m venv venv
```

2. Once created, source the environment just created
```bash
source venv/bin/activate
```

3. Once the environment has been sourced, the additional dependencies needed for the project can be installed using the following command with the requirements.txt file,
which contain all of the packages needed for installation
```bash
pip install -r requirements.txt
```

4. Once the requirements are installed, we can double check all requirements were installed successfully
```bash
pip list
```

## Environment Variables Setup

To configure the Flask application with the production values, create a `.env` file inside the `/app` directory with the following values:
```
SQLITE_DATABASE_LOCATION='../db/vehicles.db'
SQL_SETUP='../db/schema.sql'
IMPORT_SQL='../db/import_data.sql'
DEPLOYMENT_ENV="prod"
```
---

# Running the Application
To start the Flask application,

1. Go to the /app directory
```
# From the project root directory
cd app
```

2. Run the Flask Application
```bash
python app.py
```

The API will start at:
```
http://127.0.0.1:5000
```
---

# Testing the Application

## Running Unit Tests
Tests are located in the `/tests` directory.
Before running the tests, the virtual environment must be set up. Please read the 'Setup Python Environment' section for more information.

The following steps can be followed in order to run the tests properly.
1. Navigate to the /tests folder from the project root folder
```
cd tests
```

2. Run the tests.py file using pytest
```bash
pytest tests.py
```
---

## Manually Testing Endpoints via Command Line and curl requests
Once the Flask application is running, the following commands can be used in order to test the different endpoints

```bash
# 1. GET all vehicles
curl -v -X GET http://127.0.0.1:5000/vehicle  -H "Accept: application/json"

# 2. POST create a new vehicle
curl -v -X POST http://127.0.0.1:5000/vehicle  -H "Content-Type: application/json"      -d '{
           "manufacturer_name": "Honda",
           "description": "Reliable sedan",
           "horse_power": 158,
           "model_name": "Civic",
           "model_year": 2025,
           "purchase_price": 23500.50,
           "fuel_type": "gasoline"
         }'

# 3. GET a specific vehicle by VIN
curl -v -X GET http://127.0.0.1:5000/vehicle/<VIN_HERE>  -H "Accept: application/json"

# 4. PUT update a vehicle by VIN
curl -v -X PUT http://127.0.0.1:5000/vehicle/<VIN_HERE>  -H "Content-Type: application/json"  -d '{
           "manufacturer_name": "Honda",
           "description": "Updated vehicle description",
           "horse_power": 180,
           "model_name": "Civic Sport",
           "model_year": 2025,
           "purchase_price": 24999.99,
           "fuel_type": "gasoline"
         }'

# 5. DELETE a vehicle by VIN
curl -v -X DELETE http://127.0.0.1:5000/vehicle/<VIN_HERE>
```
---
