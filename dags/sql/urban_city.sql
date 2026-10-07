CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.urban_city_requests (
	request_id BIGINT PRIMARY KEY,
    created_date TIMESTAMP,
    closed_date TIMESTAMP,
    agency VARCHAR(50),
    agency_name TEXT,
    problem TEXT,
    problem_detail TEXT,
    additional_details TEXT,
    location_type VARCHAR(100),
    incident_zip VARCHAR(10),
    incident_address TEXT,
    city VARCHAR(100),
    borough VARCHAR(100),
    status VARCHAR(50),
    resolution_description TEXT,
    resolution_updated_date TIMESTAMP,
    community_board VARCHAR(100),
    council_district INTEGER,
    police_precinct INTEGER,
    channel VARCHAR(50),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);