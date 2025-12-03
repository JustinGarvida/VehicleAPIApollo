from flask import Flask, make_response, jsonify, request
import sqlite3
import uuid
import os
from dotenv import load_dotenv
import logging

app = Flask(__name__)

# Initlaize Environmental Variables
load_dotenv()
VEHICLE_DB = os.environ.get("SQLITE_DATABASE_LOCATION")
SETUP_SQL = os.environ.get("SQL_SETUP")
DEPLOYMENT_ENV = os.environ.get("DEPLOYMENT_ENV")
IMPORT_SQL = os.environ.get("IMPORT_SQL")

if not VEHICLE_DB:
    raise RuntimeError('The SQLITE_DATABASE_LOCATION is not set properly')

if not SETUP_SQL:
    raise RuntimeError('Setup SQL File is not specified')

def db_connection():
    '''
    Purpose: 
        This function is used to establsih a connection with the SQLite Database.
    Returns: 
        Connection object used to interact with the database
    '''
    try:
        conn = sqlite3.connect(VEHICLE_DB)
        conn.row_factory = sqlite3.Row
        logging.debug('Successfully connected to the SQLite Database!')
        return conn

    except Exception as error:
        raise

def validate_payload(request_payload: dict):
    '''
    Purpose: 
        This function will validate the request body passed in to ensure that the fields exist and are formatted properly.
        This will help the API determine whether to return a 422 error based on the contents of the payload
    Return: 
        Boolean indicating whether the payload has passed the validation.
        False = Did not pass validation
        True = Did pass validation
    '''
    try:
        required_fields = {
            "manufacturer_name": str,
            "description": str,
            "horse_power": int,
            "model_name": str,
            "model_year": int,
            "purchase_price": float,
            "fuel_type": str
        }

        expected_field_count = len(required_fields)

        error_encountered = False
        error_message = None
        fields_encountered = 0

        for request_key, request_value in request_payload.items():
            # Check if the field exists in the required fields
            if request_key not in required_fields:
                error_encountered = True
                error_message = f"Field {request_key} is not an expected field in the request payload"
                break;

            # Check if the field value matches the expected datatype
            field_type = required_fields[request_key]

            if not isinstance(request_value, field_type):
                error_encountered = True
                error_message = f"The value of field {request_value} does not match the expected datatype ({field_type})"
                break;
            
            fields_encountered += 1
        
        # Validate number of args matches the expected count
        if fields_encountered != expected_field_count:
            error_encountered = True
            error_message = f"The number of fields in the request payload does not match the number of expected fields"

        return not error_encountered, error_message
        
        # If we've encountered an error, we can asusme there was en error with one of the fields within the request payload, making it invalid
    except Exception:
        return False, None

    
# GET All Vehicles
@app.route("/vehicle", methods=["GET"])
def get_vehicles():
    conn = None
    cursor = None
    try:
        conn = db_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM vehicles'
        cursor.execute(query)

        rows = cursor.fetchall()
        vehicles = [dict(row) for row in rows]

        return make_response(jsonify({"data": vehicles}), 200)

    except Exception as error:
        return make_response(jsonify({"error": str(error)}), 400)
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# POST Vehicle Entry
@app.route("/vehicle", methods=["POST"])
def post_vehicle():
    conn = None
    cursor = None

    try:
        conn = db_connection()
        cursor = conn.cursor()

        if not request.is_json:
            return make_response(jsonify({"error": 'Request does not use a JSON format'}), 400)

        data = request.get_json()
        valid_data, error_message = validate_payload(data)

        if not valid_data:
            return make_response(jsonify({"error": error_message}), 422)

        generated_vin = str(uuid.uuid4())
        
        insert_query = """
        INSERT INTO vehicles (
            vin,
            manufacturer_name,
            description,
            horse_power,
            model_name,
            model_year,
            purchase_price,
            fuel_type
        ) 
        VALUES (?,?,?,?,?,?,?,?)
        RETURNING vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type
        """

        cursor.execute(insert_query, (
            generated_vin,
            data["manufacturer_name"],
            data["description"],
            data["horse_power"],
            data["model_name"],
            data["model_year"],
            data["purchase_price"],
            data["fuel_type"],)
        )

        created_vehicle = cursor.fetchone()
        conn.commit()

        if created_vehicle:
            return make_response(jsonify({"data": dict(created_vehicle)}), 201)
        else:
            return make_response(jsonify({"error": 'Vehicle could not be created'}), 500)

    except sqlite3.IntegrityError as error:
        if conn:
            conn.rollback()
        return make_response(jsonify({"error": f"Vehicle could not be created due to a constraint violation: {str(error)}"}, 422))

    except Exception as error:
        return make_response(jsonify({"error": str(error)}), 400)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
# GET Vehicle by VIN
@app.route("/vehicle/<string:vin>", methods=["GET"])
def get_vehicle_by_vin(vin):
    conn = None
    cursor = None

    try:
        conn = db_connection()
        cursor = conn.cursor()

        query = f"SELECT * FROM vehicles WHERE vin = ?"
        cursor.execute(query, (vin,))
        
        record = cursor.fetchone()

        if not record:
            return make_response(jsonify({"error": f"Vehicle with vin {vin} does not exist"}), 404)

        vehicle = [dict(record)]

        return make_response(jsonify({"data": vehicle}), 200)

    except Exception as error:
        return make_response(jsonify({"error": str(error)}), 400)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# UPDATE Vehicle by VIN
@app.route("/vehicle/<string:vin>", methods=['PUT'])
def update_vehicle(vin):
    conn = None
    cursor = None

    try:
        conn = db_connection()
        cursor = conn.cursor()

        if not request.is_json:
            return make_response(jsonify({"error": 'Request does not use a JSON format'}), 400)

        data = request.get_json()
        valid_data, error_message = validate_payload(data)

        if not valid_data:
            return make_response(jsonify({"error": error_message}), 422)

        update_query = """
            UPDATE vehicles
            SET
                manufacturer_name = ?,
                description = ?,
                horse_power = ?,
                model_name = ?,
                model_year = ?,
                purchase_price = ?,
                fuel_type = ?
            WHERE vin = ?
            RETURNING vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type
        """
        cursor.execute(
            update_query, (
                data["manufacturer_name"],
                data["description"],
                data["horse_power"],
                data["model_name"],
                data["model_year"],
                data["purchase_price"],
                data["fuel_type"],
                vin,
            )
        )

        updated_vehicle = cursor.fetchone()

        conn.commit()

        if updated_vehicle:
            return make_response(jsonify({"data": dict(updated_vehicle)}), 200)
        else:
            return make_response(jsonify({"error": f'Vehicle with vin {vin} does not exist in the database.'}), 422)

    except Exception as error:
        return make_response(jsonify({"error": str(error)}), 400)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# DELETE Vehicle by VIN
@app.route("/vehicle/<string:vin>", methods=['DELETE'])
def delete_vehicle(vin):
    conn = None
    cursor = None
    try:
        conn = db_connection()
        cursor = conn.cursor()

        delete_query = """
        DELETE FROM vehicles
        WHERE vin = ?
        """

        cursor.execute(delete_query, (vin,))
        deleted_rows = cursor.rowcount
        conn.commit()

        if deleted_rows == 0:
            return make_response(jsonify({"error": f"Vehicle with vin {vin} does not exist within the database"}), 404)
        
        return make_response("", 204)
    
    except Exception as error:
        return make_response(jsonify({"error": f"Internal server error: {str(error)}"}),500)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def init_db_core():
    """
    Core DB initialization logic:
    - Always runs SETUP_SQL to (re)create schema.
    - If DEPLOYMENT_ENV == "prod" and IMPORT_SQL is valid,
      runs IMPORT_SQL to seed data.
    This function can be safely called from tests.
    """
    if not os.path.exists(SETUP_SQL):
        raise RuntimeError(f"SQL setup file does not exist: {SETUP_SQL}")

    conn = db_connection()
    cursor = conn.cursor()

    try:
        with open(SETUP_SQL, "r") as f:
            sql_script = f.read()
        cursor.executescript(sql_script)

        if DEPLOYMENT_ENV == "prod":
            if not IMPORT_SQL or not os.path.exists(IMPORT_SQL):
                raise RuntimeError(f"IMPORT_SQL is not set or file does not exist: {IMPORT_SQL}")
            with open(IMPORT_SQL, "r") as f:
                import_script = f.read()
            cursor.executescript(import_script)

        conn.commit()
    finally:
        cursor.close()
        conn.close()


@app.cli.command("init-db")
def init_db_command():
    try:
        init_db_core()
    except Exception as error:
        print("Failed to initialize DB:", error)

if __name__ == "__main__":
    if not os.path.exists(VEHICLE_DB):
        print("Database does not exist. Creating database with dummy data")
        init_db_core()
    else:
        print("Database already exists. Starting Flask app...")
    app.run(debug=True, port=5000)
