DROP TABLE IF EXISTS vehicles;

CREATE TABLE vehicles (
    vin TEXT PRIMARY KEY COLLATE NOCASE,
    manufacturer_name TEXT,
    description TEXT,
    horse_power INTEGER,
    model_name TEXT,
    model_year INTEGER,
    purchase_price REAL,
    fuel_type TEXT
);
