-- Drop the database if it already exists
DROP DATABASE IF EXISTS gans_local;

-- Create the database
CREATE DATABASE gans_local;

-- Use the database
USE gans_local;

-- Create the 'cities' table
CREATE TABLE cities (
    city_id INT AUTO_INCREMENT,             -- Automatically generated ID for each city
    city VARCHAR(255) NOT NULL,  
    country VARCHAR(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    PRIMARY KEY (city_id)                   -- Primary key to uniquely identify each city
);

-- Create the 'population' table
CREATE TABLE population (
    city_id INT NOT NULL,
    population INT NOT NULL,                          -- Population
    timestamp_population DATE NOT NULL,               -- Year or full date
    PRIMARY KEY (city_id, timestamp_population),      -- Composite primary key
    FOREIGN KEY (city_id) REFERENCES cities(city_id)  -- Foreign key constraint
);

CREATE TABLE weather (
	weather_id INT AUTO_INCREMENT,
    city_id INT NOT NULL, 
    forecast_time DATETIME,
    outlook VARCHAR(255),
    temperature FLOAT,
    rain_in_last_3h FLOAT,
    wind_speed FLOAT,
    rain_prob FLOAT,
    data_retrieved_at DATETIME,
    PRIMARY KEY (weather_id),
    FOREIGN KEY (city_id) REFERENCES cities(City_id)
);

CREATE TABLE airports(
    city_id INT NOT NULL,
    icao VARCHAR(10),
    municipality_name VARCHAR(255),
    PRIMARY KEY (icao),
    FOREIGN KEY (city_id) REFERENCES cities(City_id)
);

CREATE TABLE flights(
    flight_id INT AUTO_INCREMENT,
    arrival_airport_icao VARCHAR(10),
    departure_airport_icao VARCHAR(10),
    departure_airport_name VARCHAR(100),
    scheduled_arrival_time DATETIME,
    flight_number VARCHAR(30),
    data_retrieved_at DATETIME,
    PRIMARY KEY (flight_id),
    FOREIGN KEY (arrival_airport_icao) REFERENCES airports(icao)
);


