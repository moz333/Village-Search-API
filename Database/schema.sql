--COUNTRY
CREATE TABLE country (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- STATE
CREATE TABLE state (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
	country_id INT REFERENCES country(id)
);
--DISTRICT
CREATE TABLE district
(
id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL,
code VARCHAR(20) UNIQUE NOT NULL,
state_id INT REFERENCES state(id),
UNIQUE(code, state_id)
)

--SUB_DISTRICT
CREATE TABLE sub_district
(
id SERIAL PRIMARY KEY,
name VARCHAR(10) NOT NULL,
code VARCHAR(20) UNIQUE NOT NULL,
district_id INT REFERENCES district(id),
UNIQUE(code, district_id)
)

--VILLAGE
CREATE TABLE village
(
id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL,
code VARCHAR(20) UNIQUE NOT NULL,
sub_district_id INT REFERENCES sub_district(id)
)


--INSERT
INSERT INTO country (name)
values('India');




