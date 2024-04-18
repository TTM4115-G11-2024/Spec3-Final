from fastapi import APIRouter
from sqlalchemy.orm import Session
import schemas
from database import get_db
from fastapi import Depends, HTTPException
import crud
from mqtt import MQTTClient

router = APIRouter()

mqtt_client = MQTTClient()
mqtt_client.start()

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


@router.post("/chargers/{charger_id}/activate/", status_code=200)
def activate_charger(activate_charger: schemas.ActivateCharger, charger_id: int, db: Session = Depends(get_db)):
    # Check if charger is valid
    db_charger = crud.get_charger(db, charger_id)
    if db_charger is None:
        raise HTTPException(status_code=404, detail="Charger not found")
    
    # Check of car is valid
    db_car = crud.get_car(db, car_id=activate_charger.car_id)
    if db_car is None:
        raise HTTPException(status_code=400, detail="Car not found")
    
    if not db_charger.is_available:
        raise HTTPException(status_code=400, detail="Charger currently is unavailable")
    
    if not db_charger.is_reservable:
        car_id = activate_charger.car_id
        # check if specified car can charge at charger
        raise HTTPException(status_code=400, detail="Charging for reservable chargers not implemented yet.")
    else:
        crud.update_charger(db, charger_id, schemas.ChargerUpdate(is_available=False, is_reservable=None))

    # inform charger and car to start charging process
    mqtt_client.send_start_charging_to_car(charger_id, activate_charger.car_id)
    mqtt_client.send_start_charging_to_charger(charger_id, activate_charger.car_id, activate_charger.target_percentage)


@router.post("/chargers/{charger_id}/deactivate/", status_code=200)
def activate_charger(charger_id: int, db: Session = Depends(get_db)):
    # Check if charger is valid
    db_charger = crud.get_charger(db, charger_id)
    if db_charger is None:
        raise HTTPException(status_code=404, detail="Charger not found")

    if db_charger.is_available:
        raise HTTPException(status_code=404, detail="Charger is currently available")
    
    crud.update_charger(db, charger_id, schemas.ChargerUpdate(is_available=True, is_reservable=None))


# Charging Station
@router.get("/stations/{station_id}", response_model=schemas.ChargingStation)
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