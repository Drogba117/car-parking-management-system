from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.database import get_db, User, ParkingSpot, Reservation, Trip
from app.auth import create_token, get_current_user

router = APIRouter()

#Pydantic схемалар

class RegisterBody(BaseModel):
    name: str
    phone: str
    plate: str

class LoginBody(BaseModel):
    phone: str

class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    plate: str
    model_config = {"from_attributes": True}

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class SpotOut(BaseModel):
    id: str
    floor: str
    row: str
    col: int
    status: str
    ev: bool
    spot_type: str
    rate: str
    model_config = {"from_attributes": True}

class ResOut(BaseModel):
    id: int
    spot_id: str
    started_at: datetime
    model_config = {"from_attributes": True}

class TripOut(BaseModel):
    id: int
    spot_label: str
    floor: str
    spot_type: str
    ev: bool
    rate: str
    duration_min: int
    cost: float
    ended_at: datetime
    model_config = {"from_attributes": True}

class FloorOcc(BaseModel):
    floor: str
    total: int
    free: int
    pct_occupied: int

class OccOut(BaseModel):
    free_total: int
    floors: list[FloorOcc]
 

@router.post("/api/register", response_model=TokenOut)
def register(body: RegisterBody, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == body.phone).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Phone already registered")
    user = User(name=body.name, phone=body.phone, plate=body.plate.upper())
    db.add(user); db.commit(); db.refresh(user)
    return TokenOut(access_token=create_token(user.id), user=UserOut.model_validate(user))

@router.post("/api/login", response_model=TokenOut)
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == body.phone).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return TokenOut(access_token=create_token(user.id), user=UserOut.model_validate(user))

@router.get("/api/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current


@router.get("/api/spots", response_model=list[SpotOut])
def get_spots(
    floor: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(ParkingSpot)
    if floor:
        q = q.filter(ParkingSpot.floor == floor.upper())
    return q.all()

@router.get("/api/spots/occupancy", response_model=OccOut)
def occupancy(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    all_spots = db.query(ParkingSpot).all()
    data: dict = {}
    for s in all_spots:
        f = s.floor
        if f not in data:
            data[f] = {"floor": f, "total": 0, "free": 0}
        data[f]["total"] += 1
        if s.status == "free":
            data[f]["free"] += 1
    floors = [
        FloorOcc(
            floor=v["floor"], total=v["total"], free=v["free"],
            pct_occupied=round((v["total"]-v["free"])/v["total"]*100)
        )
        for v in data.values()
    ]
    free_total = sum(v["free"] for v in data.values())
    return OccOut(free_total=free_total, floors=floors)

@router.get("/api/my-reservation", response_model=Optional[SpotOut])
def my_reservation(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    res = db.query(Reservation).filter(Reservation.user_id == current.id).first()
    return res.spot if res else None

@router.post("/api/spots/{spot_id}/reserve", response_model=ResOut)
def reserve(spot_id: str, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    if db.query(Reservation).filter(Reservation.user_id == current.id).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already have a reservation")
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Spot not found")
    if spot.status != "free":
        raise HTTPException(status.HTTP_409_CONFLICT, "Spot is not free")
    spot.status = "reserved"
    res = Reservation(user_id=current.id, spot_id=spot_id)
    db.add(res); db.commit(); db.refresh(res)
    return res

@router.delete("/api/spots/{spot_id}/reserve", response_model=TripOut)
def release(spot_id: str, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    res = db.query(Reservation).filter(
        Reservation.user_id == current.id,
        Reservation.spot_id == spot_id,
    ).first()
    if not res:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reservation not found")
    spot = res.spot
    now  = datetime.utcnow()
    dur  = max(1, int((now - res.started_at).total_seconds() / 60))
    rate_num = float(spot.rate.replace("$","").replace("/hr",""))
    cost = round(rate_num * dur / 60, 2)
    trip = Trip(
        user_id=current.id, spot_label=spot.floor+spot.row+str(spot.col),
        floor=spot.floor, spot_type=spot.spot_type, ev=spot.ev,
        rate=spot.rate, duration_min=dur, cost=cost, ended_at=now,
    )
    db.add(trip)
    spot.status = "free"
    db.delete(res)
    db.commit(); db.refresh(trip)
    return trip


@router.get("/api/trips", response_model=list[TripOut])
def trips(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    return (
        db.query(Trip)
        .filter(Trip.user_id == current.id)
        .order_by(Trip.ended_at.desc())
        .all()
    )
