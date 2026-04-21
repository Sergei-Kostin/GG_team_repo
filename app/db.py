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
                created_at TIMESTAMP DEFAULT now()
            );
            ALTER TABLE hotel_rooms ADD COLUMN IF NOT EXISTS room_type VARCHAR(50);
            ALTER TABLE hotel_rooms ADD COLUMN IF NOT EXISTS price numeric(10, 2) NOT NULL DEFAULT 0;

            CREATE TABLE IF NOT EXISTS hotel_guests (
                id SERIAL PRIMARY KEY,
                firstname VARCHAR(100) NOT NULL,
                lastname VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT now()
            );
            ALTER TABLE hotel_guests ADD COLUMN IF NOT EXISTS address VARCHAR(255);

            CREATE TABLE IF NOT EXISTS hotel_bookings (
                id SERIAL PRIMARY KEY,
                guest_id INT REFERENCES hotel_guests(id),
                room_id INT REFERENCES hotel_rooms(id),
                created_at TIMESTAMP DEFAULT now()
            );
            ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS datefrom TIMESTAMP NOT NULL DEFAULT now();
            ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS dateto TIMESTAMP NOT NULL DEFAULT now() + interval '1 day';
            ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS addinfo VARCHAR(255);
            ALTER TABLE hotel_bookings ALTER COLUMN datefrom SET DEFAULT now();
            ALTER TABLE hotel_bookings ALTER COLUMN dateto SET DEFAULT now() + interval '1 day';
        """)


