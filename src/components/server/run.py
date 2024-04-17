from fastapi import FastAPI
import uvicorn
import endpoints
import models
from database import SessionLocal, engine

def run():
    print("Hello from server")
    models.Base.metadata.create_all(bind=engine)

    app = FastAPI()
    app.include_router(endpoints.router)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

run()