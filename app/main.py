from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# main endpoint for this API
my_name = "Sergei"



@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    my_IP = request.client.host
    return f"<h1>Hello, your ip is {my_IP}</h1>"

@app.get("/")
def read_root():
    return {"msg": f"Hello, {my_name}"}


