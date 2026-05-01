import pyodbc


CONNECTION_STRING = (
    "DRIVER={SQL Server};"
    "SERVER=DESKTOP-H16PTFL\\SQLEXPRESS;"
    "DATABASE=healthcarepdb;"
    "Trusted_Connection=yes;"
)

HEALTHCARE_TABLE_CANDIDATES = [
    "dbo.healthcarepdb",
    "dbo.healthcare",
    "healthcarepdb",
    "healthcare",
    "HealthCarePDB",
]

USER_TABLE_CANDIDATES = ["dbo.users", "users", "Users"]


def get_connection():
    return pyodbc.connect(CONNECTION_STRING)


def _list_tables(cursor):
    cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    return [f"{row[0]}.{row[1]}" for row in cursor.fetchall()]


def _resolve_table_name(cursor, candidates):
    available_tables = _list_tables(cursor)
    lookup = {table.lower(): table for table in available_tables}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    for candidate in candidates:
        short_name = candidate.split(".")[-1].lower()
        for table in available_tables:
            if table.split(".")[-1].lower() == short_name:
                return table
    return None


def _resolve_user_table(cursor):
    return _resolve_table_name(cursor, USER_TABLE_CANDIDATES)


def get_healthcare_table():
    with get_connection() as connection:
        cursor = connection.cursor()
        table_name = _resolve_table_name(cursor, HEALTHCARE_TABLE_CANDIDATES)
        if not table_name:
            raise ValueError("No healthcare table found in SQL Server. Expected one of: " + ", ".join(HEALTHCARE_TABLE_CANDIDATES))
        return table_name


def ensure_users_table():
    with get_connection() as connection:
        cursor = connection.cursor()
        if _resolve_user_table(cursor):
            return
        cursor.execute("CREATE TABLE dbo.users (id INT IDENTITY(1,1) PRIMARY KEY, username NVARCHAR(100) NOT NULL UNIQUE, password NVARCHAR(100) NOT NULL)")
        connection.commit()


def register_user(username, password):
    ensure_users_table()
    with get_connection() as connection:
        cursor = connection.cursor()
        table_name = _resolve_user_table(cursor) or "dbo.users"
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            return False, "Username already exists."
        cursor.execute(f"INSERT INTO {table_name} (username, password) VALUES (?, ?)", (username, password))
        connection.commit()
    return True, "Registration completed successfully."


def authenticate_user(username, password):
    ensure_users_table()
    with get_connection() as connection:
        cursor = connection.cursor()
        table_name = _resolve_user_table(cursor) or "dbo.users"
        cursor.execute(f"SELECT id, username FROM {table_name} WHERE username = ? AND password = ?", (username, password))
        row = cursor.fetchone()
        if not row:
            return None
        return {"id": row[0], "username": row[1]}


def insert_healthcare_record(record):
    table_name = get_healthcare_table()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO {table_name} (
                hospital_id, hospital_name, hospital_city, doctor, doctor_id,
                specialist, patient_id, patient_name, disease, floor,
                medical_condition, admitted_date, room_number,
                discharge_date, bill_amount
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["hospital_id"], record["hospital_name"], record["hospital_city"], record["doctor"], record["doctor_id"],
                record["specialist"], record["patient_id"], record["patient_name"], record["disease"], record["floor"],
                record["medical_condition"], record["admitted_date"], record["room_number"], record["discharge_date"], record["bill_amount"],
            ),
        )
        connection.commit()


def fetch_overview_metrics():
    table_name = get_healthcare_table()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT COUNT(*), COUNT(DISTINCT patient_id), COUNT(DISTINCT hospital_name), COUNT(DISTINCT doctor),
                   COUNT(DISTINCT disease), COUNT(DISTINCT specialist),
                   SUM(CAST(bill_amount AS FLOAT)), AVG(CAST(bill_amount AS FLOAT))
            FROM {table_name}
            """
        )
        row = cursor.fetchone()
        return {
            "total_records": int(row[0] or 0),
            "total_patients": int(row[1] or 0),
            "total_hospitals": int(row[2] or 0),
            "total_doctors": int(row[3] or 0),
            "total_diseases": int(row[4] or 0),
            "total_specialists": int(row[5] or 0),
            "total_bill": float(row[6] or 0),
            "average_bill": float(row[7] or 0),
        }


def fetch_group_counts(column_name):
    table_name = get_healthcare_table()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT CAST({column_name} AS NVARCHAR(255)) AS label, COUNT(*) AS total
            FROM {table_name}
            WHERE {column_name} IS NOT NULL AND LTRIM(RTRIM(CAST({column_name} AS NVARCHAR(255)))) <> ''
            GROUP BY {column_name}
            ORDER BY label ASC
            """
        )
        return [{"label": row[0], "total": int(row[1])} for row in cursor.fetchall()]


def fetch_bill_by_group(column_name):
    table_name = get_healthcare_table()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT CAST({column_name} AS NVARCHAR(255)) AS label, SUM(CAST(bill_amount AS FLOAT)) AS total
            FROM {table_name}
            WHERE {column_name} IS NOT NULL AND LTRIM(RTRIM(CAST({column_name} AS NVARCHAR(255)))) <> ''
            GROUP BY {column_name}
            ORDER BY label ASC
            """
        )
        return [{"label": row[0], "total": float(row[1] or 0)} for row in cursor.fetchall()]


def fetch_detailed_records(limit=None):
    table_name = get_healthcare_table()
    with get_connection() as connection:
        cursor = connection.cursor()
        top_clause = f"TOP {int(limit)} " if limit else ""
        cursor.execute(
            f"""
            SELECT {top_clause}
                hospital_id,
                hospital_name,
                hospital_city,
                doctor,
                doctor_id,
                specialist,
                patient_id,
                patient_name,
                disease,
                floor,
                medical_condition,
                admitted_date,
                room_number,
                discharge_date,
                bill_amount
            FROM {table_name}
            ORDER BY admitted_date DESC, patient_id DESC
            """
        )
        return [
            {
                "hospital_id": row[0],
                "hospital_name": row[1],
                "hospital_city": row[2],
                "doctor": row[3],
                "doctor_id": row[4],
                "specialist": row[5],
                "patient_id": row[6],
                "patient_name": row[7],
                "disease": row[8],
                "floor": row[9],
                "medical_condition": row[10],
                "admitted_date": str(row[11]),
                "room_number": row[12],
                "discharge_date": str(row[13]),
                "bill_amount": float(row[14] or 0),
            }
            for row in cursor.fetchall()
        ]


def fetch_recent_records(limit=12):
    return fetch_detailed_records(limit=limit)
