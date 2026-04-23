import os, psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return psycopg.connect(DATABASE_URL, autocommit=True, row_factory=psycopg.rows.dict_row)

def create_schema():
    with get_conn() as conn, conn.cursor() as cur:
        # Create the schema
        cur.execute("""
            -- Add pgcrypto
            CREATE EXTENSION IF NOT EXISTS pgcrypto;
                    
            ----------
            -- ROOMS
            ----------
            CREATE TABLE IF NOT EXISTS hotel_rooms (
                id SERIAL PRIMARY KEY,
                room_number INT NOT NULL,
                room_type VARCHAR,
                price NUMERIC NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT now()
            );

            ----------
            -- Guests
            ----------
            CREATE TABLE IF NOT EXISTS hotel_guests (
                id SERIAL PRIMARY KEY,
                firstname VARCHAR NOT NULL,
                lastname VARCHAR NOT NULL,
                address VARCHAR,
                api_key VARCHAR DEFAULT encode(gen_random_bytes(32), 'hex'),
                created_at TIMESTAMP DEFAULT now()
            );

            ----------
            -- Bookings
            ----------
            CREATE TABLE IF NOT EXISTS hotel_bookings (
                id SERIAL PRIMARY KEY,
                guest_id INT NOT NULL REFERENCES hotel_guests(id),
                room_id INT NOT NULL REFERENCES hotel_rooms(id),
                datefrom DATE NOT NULL DEFAULT now(),
                dateto DATE NOT NULL DEFAULT now()::date+1,
                info VARCHAR,
                stars INT CHECK (stars >= 1 AND stars <= 5),
                created_at TIMESTAMP DEFAULT now()
            );
            
            -- Add stars column if it doesn't exist
            ALTER TABLE hotel_bookings
            ADD COLUMN IF NOT EXISTS stars INT CHECK (stars >= 1 AND stars <= 5);
        """)

if __name__ == "__main__":
    create_schema()
    print("Schema created successfully")