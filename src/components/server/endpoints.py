from fastapi import APIRouter
from sqlalchemy.orm import Session
import schemas
from database import get_db
from fastapi import Depends, HTTPException
import crud

router = APIRouter()

# Car
@router.get("/cars/{car_id}", response_model=schemas.Car)
def get_car(car_id: str, db: Session = Depends(get_db)):
    db_car = crud.get_car(db, car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car


@router.post("/cars/", response_model=schemas.Car)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    db_car = crud.get_car(db, car_id=car.id)
    if db_car is not None:
        raise HTTPException(status_code=400, detail="Car already exists")
    return crud.create_car(db, car)


# Charger
@router.get("/chargers/{charger_id}", response_model=schemas.Charger)
def get_charger(charger_id: int, db: Session = Depends(get_db)):
    db_charger = crud.get_charger(db, charger_id)
    if db_charger is None:
        raise HTTPException(status_code=404, detail="Charger not found")
    return db_charger


@router.post("/chargers/", response_model=schemas.Charger)
def create_charger(charger: schemas.ChargerCreate, db: Session = Depends(get_db)):
    db_station = crud.get_charging_station(db, charger.station_id)
    if db_station is None:
        raise HTTPException(status_code=400, detail="Station of station_id does not exist")
    
    return crud.create_charger(db, charger)


# Charging Station
@router.get("/stations/{station_id}", response_model=schemas.Charger)
def get_station(station_id: int, db: Session = Depends(get_db)):
    db_station = crud.get_charging_station(db, station_id)
    if db_station is None:
        raise HTTPException(status_code=404, detail="Charging station not found")
    return db_station


@router.post("/stations/", response_model=schemas.ChargingStation)
def create_station(db: Session = Depends(get_db)):
    return crud.create_charging_station(db)


# Reservation
@router.get("/reservations/{reservation_id}", response_model=schemas.Reservation)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return db_reservation


@router.post("/reservations/", response_model=schemas.Reservation)
def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    db_car = crud.get_car(db, car_id=reservation.car_id)
    if db_car is None:
        raise HTTPException(status_code=400, detail="Car of car_id does not exist")
    
    db_charger = crud.get_charger(db, reservation.charger_id)
    if db_charger is None:
        raise HTTPException(status_code=404, detail="Charger of charger_id does not exist")
    return crud.create_reservation(db, reservation)