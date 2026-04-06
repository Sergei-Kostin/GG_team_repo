import os, psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg.connect(DATABASE_URL, autocommit=True, row_factory=psycopg.rows.dict_row)

def create_schema():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS hotel_rooms (
                id SERIAL PRIMARY KEY,
                room_number int NOT NULL,
                room_type VARCHAR(50) NOT NULL,
                price numeric(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT now()
            );
            CREATE TABLE IF NOT EXISTS hotel_guests (
                id SERIAL PRIMARY KEY,
                firstname VARCHAR(100) NOT NULL,
                lastname VARCHAR(100) NOT NULL,
                address VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT now()
            );
            CREATE TABLE IF NOT EXISTS hotel_bookings (
                id SERIAL PRIMARY KEY,
                guest_id INT REFERENCES hotel_guests(id),
                room_id INT REFERENCES hotel_rooms(id),
                datefrom TIMESTAMP NOT NULL,
                dateto TIMESTAMP NOT NULL,
                addinfo VARCHAR(255),
                created_at TIMESTAMP DEFAULT now()
            );
        """)



