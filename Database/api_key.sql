CREATE TABLE api_key (
id SERIAL PRIMARY KEY,
api_key VARCHAR (100) UNIQUE NOT NULL,
name VARCHAR (100) 
)

INSERT INTO api_key (api_key, name)
VALUES('abc123', 'testUser')

SELECT * FROM api_key