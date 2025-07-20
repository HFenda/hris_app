from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the HRIS API"}

@app.get("/hello")
async def read_root():
    return {"message": "Hello HRIS"}