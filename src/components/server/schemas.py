from pydantic import BaseModel
from datetime import datetime

# Reservation
class ReservationBase(BaseModel):
    start_time: datetime
    end_time: datetime
    car_id: str
    charger_id: int

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int

    class Config:
        orm_mode = True

# Car
class BaseCar(BaseModel):
    id: str

class CarCreate(BaseCar):
    pass

class Car(BaseCar):
    reservations: list[Reservation]

    class Config:
        orm_mode = True



# Charger
class ChargerBase(BaseModel):
    is_reservable: bool
    station_id: int


class ChargerCreate(ChargerBase):
    pass


class Charger(ChargerBase):
    id: int
    reservations: list[Reservation]

    class Config:
        orm_mode = True

# Charger Station
class ChargingStation(BaseModel):
    id: int

    class Config:
        orm_mode = True
