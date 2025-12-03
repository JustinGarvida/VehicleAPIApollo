-- Use this function to insert dummy vehicles into the vehicles database for production use
INSERT INTO vehicles (
    vin, manufacturer_name, description, horse_power,
    model_name, model_year, purchase_price, fuel_type
) VALUES
('TESTVIN001', 'Honda', 'Compact sedan', 158, 'Civic', 2020, 22000.00, 'Gasoline'),
('TESTVIN002', 'Toyota', 'Reliable midsize', 203, 'Camry', 2021, 26000.00, 'Gasoline'),
('TESTVIN003', 'Tesla', 'Electric sedan', 450, 'Model 3', 2022, 39999.99, 'Electric'),
('TESTVIN004', 'Ford', 'Popular pickup', 290, 'F-150', 2019, 32000.00, 'Gasoline');
