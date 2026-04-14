from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.db import get_conn
from app.db import create_schema
app = FastAPI()

# main endpoint for this API
my_name = "Sergei"

hotel_rooms = [
    { "room_number": "101", "room_type": "1 person", "price": 100 },
    { "room_number": "102", "room_type": "2 persons", "price": 150 },
    { "room_number": "103", "room_type": "3 persons", "price": 200 },
]

origins = [
    "http://127.0.0.1:5500",
    "https://gg-team-repo-git-web-communication-and-databases-1.2.rahtiapp.fi",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_schema()

@app.get("/api/rooms")
def get_rooms():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM hotel_rooms")
        rows = cur.fetchall()
        return {"hotel_rooms": rows}

@app.post("/api/booking")
def create_booking():
    return {"msg": "Booking created"}

@app.get("/api/ip", response_class=HTMLResponse)
def read_root(request: Request):
    my_IP = request.client.host
    return f"{my_IP}"

@app.get("/")
def read_root():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT version()")
        result = cur.fetchone()
        return {"db_status":result}
    

@app.get("/if/{term}")
def if_test(term: str):
    msg = "default msg"
    if term == "hello" or term == "hi":
        msg = "Hello yourself!"

    elif term == "Hej" or term == "Moi":
        msg = "Hej pa dig!"
    else:
        msg = "I don't understand you"
        
    return {"msg": msg}
