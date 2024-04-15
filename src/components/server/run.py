from fastapi import FastAPI
import uvicorn
import components.server.crud as crud

def run():
    print("Hello from server")
    app = FastAPI()
    app.include_router(crud.router)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")