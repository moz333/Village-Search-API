from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_conn():
    return psycopg2.connect(
        dbname="village_db",
        user="postgres",
        password="@Kiliyam6",
        host="localhost",
        port="5432"
    )

# -----------------------------
# API KEY VERIFICATION
# -----------------------------
def verify_api_key(x_api_key: str):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM api_key
        WHERE api_key = %s
    """, (x_api_key,))

    data = cur.fetchone()

    cur.close()
    conn.close()

    if not data:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

# -----------------------------
# GET ALL STATES
# -----------------------------
@app.get("/states")
def get_states(x_api_key: str = Header(...)):

    verify_api_key(x_api_key)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name
        FROM state
        ORDER BY name
        """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in data
    ]

# -----------------------------
# GET DISTRICTS BY STATE
# -----------------------------
@app.get("/districts")
def get_districts(
    state_id: int,
    x_api_key: str = Header(...)
):

    verify_api_key(x_api_key)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name
        FROM district
        WHERE state_id = %s
        ORDER BY name
        LIMIT 100
    """, (state_id,))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in data
    ]

# -----------------------------
# GET SUBDISTRICTS
# -----------------------------
@app.get("/subdistricts")
def get_subdistricts(
    district_id: int,
    x_api_key: str = Header(...)
):

    verify_api_key(x_api_key)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name
        FROM sub_district
        WHERE district_id = %s
        ORDER BY name
        LIMIT 100
    """, (district_id,))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in data
    ]

# -----------------------------
# GET VILLAGES
# -----------------------------
@app.get("/villages")
def get_villages(
    subdistrict_id: int,
    x_api_key: str = Header(...)
):

    verify_api_key(x_api_key)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name
        FROM village
        WHERE sub_district_id = %s
        ORDER BY name
        LIMIT 100
    """, (subdistrict_id,))
   

    data = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in data
    ]

# -----------------------------
# SEARCH API
# -----------------------------
@app.get("/search")
def search(
    q: str,
    page: int = 1,
    limit: int = 20,
    x_api_key: str = Header(...)
):
    start_time = time.time()
    
    verify_api_key(x_api_key)

    offset = (page - 1) * limit

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            v.name,
            sd.name,
            d.name,
            s.name
        FROM village v
        JOIN sub_district sd
            ON v.sub_district_id = sd.id
        JOIN district d
            ON sd.district_id = d.id
        JOIN state s
            ON d.state_id = s.id
        WHERE v.name ILIKE %s
        LIMIT %s OFFSET %s
    """, (f"%{q}%", limit, offset))

    data = cur.fetchall()

    cur.close()
    conn.close()

    print ("response time:", time.time()-start_time)
    
    return [
        {
            "village": row[0],
            "subdistrict": row[1],
            "district": row[2],
            "state": row[3]
        }
        for row in data
    ]