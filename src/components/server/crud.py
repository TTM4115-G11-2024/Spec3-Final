from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
async def root():
    return {"message": "Hello World"}