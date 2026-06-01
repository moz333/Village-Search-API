import pandas as pd
import psycopg2
import os

def find_col(cols, keyword):
    for c in cols:
        if keyword.lower() in c.lower():
            return c
    return None

conn = psycopg2.connect(
    dbname="village_db",
    user="postgres",
    password="@Kiliyam6",
    host="localhost",
    port="5432"
)

cur = conn.cursor()
print("script started")

folder_path = r"C:\zubair\Data Analysis\capstone\all-india-villages-master-list-excel\dataset"

for file in os.listdir(folder_path):
    if not (file.endswith(".xls") or file.endswith(".xlsx")):
        continue

    file_path = os.path.join(folder_path, file)
    print(f"Processing {file}...")

    # -----------------------------
    # STEP 1: Try normal header detection
    # -----------------------------
    header_found = False

    for i in range(5):
        df = pd.read_excel(file_path, header=i)
        df.columns = df.columns.astype(str).str.strip()

        if any('STC' in c for c in df.columns):
            header_found = True
            break

    # -----------------------------
    # STEP 2: If header found → normal processing
    # -----------------------------
    if header_found:
        df.columns = (
            df.columns
            .str.strip()
            .str.replace('\xa0', ' ', regex=False)
            .str.replace('\ufeff', '', regex=False)
            .str.replace(' +', ' ', regex=True)
        )

        state_col = find_col(df.columns, 'STC')
        district_col = find_col(df.columns, 'DTC')
        subdistrict_col = find_col(df.columns, 'Sub_DT')
        village_col = find_col(df.columns, 'PLCN')

        state_name_col = find_col(df.columns, 'STATE')
        district_name_col = find_col(df.columns, 'DISTRICT NAME')
        subdistrict_name_col = find_col(df.columns, 'SUB-DISTRICT')
        area_col = find_col(df.columns, 'Area')

        if None in [
            state_col, district_col, subdistrict_col, village_col,
            state_name_col, district_name_col, subdistrict_name_col, area_col
        ]:
            print(f"⚠️ Skipping file due to column mismatch: {file}")
            continue

        use_manual = False

    # -----------------------------
    # STEP 3: No header → force correct structure
    # -----------------------------
    else:
        print(f"⚠️ Fixing broken file format: {file}")

        # Try reading raw
        df = pd.read_excel(file_path, header=None)
        df = df.dropna(axis=1, how='all')

        # Try shifting rows if needed
        if df.shape[1] < 8:
            df = pd.read_excel(file_path, skiprows=1, header=None)
            df = df.dropna(axis=1, how='all')

        if df.shape[1] < 8:
            df = pd.read_excel(file_path, skiprows=2, header=None)
            df = df.dropna(axis=1, how='all')

        if df.shape[1] != 8:
            print(f"❌ Could not fix structure: {file}")
            continue

        df.columns = [
            'state_code',
            'state_name',
            'district_code',
            'district_name',
            'subdistrict_code',
            'subdistrict_name',
            'village_code',
            'village_name'
        ]

        use_manual = True

    # -----------------------------
    # STEP 4: Insert into DB
    # -----------------------------
    for _, row in df.iterrows():
        try:
            if use_manual:
                state_code = str(row['state_code']).zfill(2)
                district_code = str(row['district_code']).zfill(3)
                subdistrict_code = str(row['subdistrict_code']).zfill(5)
                village_code = str(row['village_code']).zfill(6)

                state_name = str(row['state_name']).strip()
                district_name = str(row['district_name']).strip()
                subdistrict_name = str(row['subdistrict_name']).strip()
                village_name = str(row['village_name']).strip()

            else:
                state_code = str(row[state_col]).zfill(2)
                district_code = str(row[district_col]).zfill(3)
                subdistrict_code = str(row[subdistrict_col]).zfill(5)
                village_code = str(row[village_col]).zfill(6)

                state_name = str(row[state_name_col]).strip()
                district_name = str(row[district_name_col]).strip()
                subdistrict_name = str(row[subdistrict_name_col]).strip()
                village_name = str(row[area_col]).strip()

            if not village_name or village_name.lower() == 'nan':
                continue

            # STATE
            cur.execute("""
                INSERT INTO state (name, code, country_id)
                VALUES (%s, %s, 1)
                ON CONFLICT (code) DO NOTHING
            """, (state_name, state_code))

            cur.execute("SELECT id FROM state WHERE code=%s", (state_code,))
            state_id = cur.fetchone()[0]

            # DISTRICT
            cur.execute("""
                INSERT INTO district (name, code, state_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (code, state_id) DO NOTHING
            """, (district_name, district_code, state_id))

            cur.execute("""
                SELECT id FROM district WHERE code=%s AND state_id=%s
            """, (district_code, state_id))
            district_id = cur.fetchone()[0]

            # SUB-DISTRICT
            cur.execute("""
                INSERT INTO sub_district (name, code, district_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (code, district_id) DO NOTHING
            """, (subdistrict_name, subdistrict_code, district_id))

            cur.execute("""
                SELECT id FROM sub_district WHERE code=%s AND district_id=%s
            """, (subdistrict_code, district_id))
            subdistrict_id = cur.fetchone()[0]

            # VILLAGE
            cur.execute("""
                INSERT INTO village (name, code, sub_district_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (code) DO NOTHING
            """, (village_name, village_code, subdistrict_id))

        except Exception as e:
            print(f"Error in row: {e}")
            conn.rollback()
            continue

    conn.commit()

print("✅ All data imported successfully!")

cur.close()
conn.close()