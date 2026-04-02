from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# main endpoint for this API
my_name = "Sergei"

hotel_rooms = [
    { "number": "101", "size": "1 person", "price": 100 },
    { "number": "102", "size": "2 persons", "price": 150 },
    { "number": "103", "size": "3 persons", "price": 200 },
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


@app.get("/api/rooms")
def get_rooms():
    return hotel_rooms

@app.get("/api/ip", response_class=HTMLResponse)
def read_root(request: Request):
    my_IP = request.client.host
    return f"{my_IP}"

@app.get("/")
def read_root():
    return {"msg": f"Hello, {my_name}"}


