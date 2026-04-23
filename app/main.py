from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.db import get_conn, create_schema

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_schema()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def validate_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail={"error": "API Key missing!"})
    
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM hotel_guests WHERE api_key = %s
        """, [api_key])
        guest = cur.fetchone()
        if not guest:
            raise HTTPException(status_code=401, detail={"error": "Bad API Key!"})
        return guest

# Data model for bookings
class Booking(BaseModel):
    room_id: int
    datefrom: date
    dateto: date
    info: Optional[str] = None

# Data model for review/stars
class Review(BaseModel):
    stars: int

    class Config:
        json_schema_extra = {
            "example": {"stars": 5}
        }

# Main route for this API
@app.get("/")
def read_root(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT version()")
        result = cur.fetchone()
    return {"msg": "Hotel API!", "db_status": result}

# List all guests 
@app.get("/guests")
def get_guests(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT 
                g.*,
                (SELECT count(*) 
                    FROM hotel_bookings
                    WHERE guest_id = g.id
                        AND dateto < now()
                ) as previous_visits
            FROM hotel_guests g    
            ORDER BY g.lastname
        """)
        guests = cur.fetchall()
    return guests

# List all rooms 
@app.get("/rooms")
def get_rooms(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM hotel_rooms")
        rooms = cur.fetchall()
    return rooms

# Get one room
@app.get("/rooms/{id}")
def get_one_room(id: int): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * 
            FROM hotel_rooms 
            WHERE id = %s
        """, (id,))
        room = cur.fetchone()
    return room

# List all bookings 
@app.get("/bookings")
def get_bookings(guest: dict = Depends(validate_key)): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT 
                r.room_number,
                g.firstname || ' ' || g.lastname AS guest_name,
                b.dateto::date - b.datefrom::date AS nights,
                r.price AS price_per_night,
                (b.dateto::date - b.datefrom::date) * r.price AS gross_price,
                CASE
                    WHEN (b.dateto::date - b.datefrom::date) >= 7 THEN 
                        (b.dateto::date - b.datefrom::date) * r.price * 0.8
                    ELSE (b.dateto::date - b.datefrom::date) * r.price
                END AS total_price,
                b.*
            FROM hotel_bookings b
            INNER JOIN hotel_rooms r
                ON r.id = b.room_id
            INNER JOIN hotel_guests g
                ON g.id = b.guest_id
            WHERE b.guest_id = %s
            ORDER BY b.id DESC        
        """, [guest['id']])
        bookings = cur.fetchall()
    return bookings

# Create booking
@app.post("/bookings")
def create_booking(booking: Booking, guest: dict = Depends(validate_key)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO hotel_bookings (
                room_id, 
                guest_id,
                datefrom,
                dateto,
                info
            ) VALUES (
                %s, %s, %s, %s, %s
            ) RETURNING *
        """, [
            booking.room_id, 
            guest['id'],
            booking.datefrom,
            booking.dateto,
            booking.info
        ])
        new_booking = cur.fetchone()
        
    return { 
        "msg": "Booking created!", 
        "id": new_booking['id'],
        "room_id": new_booking['room_id']
    }

# Update booking with review stars
@app.put("/bookings/{booking_id}")
def update_booking_review(booking_id: int, review: Review, guest: dict = Depends(validate_key)):
    # Validate stars are between 1 and 5
    if review.stars < 1 or review.stars > 5:
        raise HTTPException(status_code=400, detail={"error": "Stars must be between 1 and 5"})
    
    with get_conn() as conn, conn.cursor() as cur:
        # First check if booking exists and belongs to the guest
        cur.execute("""
            SELECT * FROM hotel_bookings 
            WHERE id = %s AND guest_id = %s
        """, [booking_id, guest['id']])
        booking = cur.fetchone()
        
        if not booking:
            raise HTTPException(status_code=404, detail={"error": "Booking not found or does not belong to this guest"})
        
        # Update the booking with stars
        cur.execute("""
            UPDATE hotel_bookings 
            SET stars = %s
            WHERE id = %s
            RETURNING *
        """, [review.stars, booking_id])
        updated_booking = cur.fetchone()
    
    return {
        "msg": "Review submitted successfully!",
        "id": updated_booking['id'],
        "stars": updated_booking['stars'],
        "room_id": updated_booking['room_id']
    }




