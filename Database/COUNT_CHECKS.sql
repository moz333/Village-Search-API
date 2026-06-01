SELECT COUNT(*) FROM village;
SELECT COUNT(*) FROM sub_district;
SELECT COUNT(*) FROM district;
SELECT COUNT(*) FROM state;

SELECT * FROM state LIMIT 5 
SELECT COUNT(*) FROM district
WHERE state_id = (
    SELECT id FROM state
    WHERE name ILIKE '%MADHYA%'
);
SELECT * FROM state


SELECT * FROM district
WHERE state_id = 462894