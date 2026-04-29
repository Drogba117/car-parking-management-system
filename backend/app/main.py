from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import datetime, math

from app.database import Base, engine, get_db, User, ParkingSpot, Reservation, Trip
from app.auth import create_token, get_current_user_id

# ── Create tables on startup ──────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Park API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic schemas ──────────────────────────────────────────────────────────

class RegisterBody(BaseModel):
    name:  str
    phone: str
    plate: str

class LoginBody(BaseModel):
    phone: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def user_dict(u: User):
    return {"id": u.id, "name": u.name, "phone": u.phone, "plate": u.plate}

def spot_dict(s: ParkingSpot):
    return {
        "id":     s.id,
        "floor":  s.floor,
        "row":    s.row,
        "col":    s.col,
        "status": s.status,
        "ev":     s.ev,
        "type":   s.spot_type,
        "rate":   s.rate,
    }

def trip_dict(t: Trip):
    return {
        "id":          t.id,
        "label":       t.label,
        "floor":       t.floor,
        "type":        t.spot_type,
        "ev":          t.ev,
        "rate":        t.rate,
        "duration":    t.duration_min,
        "cost":        round(t.cost, 2),
        "date":        t.ended_at.strftime("%-d %b") if t.ended_at else "",
        "time":        t.ended_at.strftime("%H:%M")  if t.ended_at else "",
    }


# ── Auth routes ───────────────────────────────────────────────────────────────

@app.post("/api/auth/register", status_code=201)
def register(body: RegisterBody, db: Session = Depends(get_db)):
    if not body.name.strip():
        raise HTTPException(400, "Name is required")
    if len(body.phone.replace(" ", "").replace("+", "").replace("-", "")) < 7:
        raise HTTPException(400, "Invalid phone number")
    if not body.plate.strip():
        raise HTTPException(400, "Plate is required")

    existing = db.query(User).filter(User.phone == body.phone).first()
    if existing:
        raise HTTPException(409, "Phone number already registered")

    user = User(name=body.name.strip(), phone=body.phone.strip(), plate=body.plate.strip().upper())
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"token": create_token(user.id), "user": user_dict(user)}


@app.post("/api/auth/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == body.phone).first()
    if not user:
        raise HTTPException(404, "No account found for this phone number")
    return {"token": create_token(user.id), "user": user_dict(user)}


# ── User route ────────────────────────────────────────────────────────────────

@app.get("/api/me")
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # active reservation
    reservation = db.query(Reservation).filter(Reservation.user_id == user_id).first()
    active_spot = None
    if reservation:
        spot = db.query(ParkingSpot).filter(ParkingSpot.id == reservation.spot_id).first()
        if spot:
            active_spot = {**spot_dict(spot), "reservation_id": reservation.id,
                           "reserved_at": reservation.started_at.isoformat()}

    return {"user": user_dict(user), "active_reservation": active_spot}


# ── Spots routes ──────────────────────────────────────────────────────────────

@app.get("/api/spots")
def get_spots(floor: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ParkingSpot)
    if floor:
        query = query.filter(ParkingSpot.floor == floor.upper())
    spots = query.all()
    return [spot_dict(s) for s in spots]


@app.post("/api/spots/{spot_id}/reserve", status_code=201)
def reserve_spot(
    spot_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # cancel existing reservation for this user
    existing_res = db.query(Reservation).filter(Reservation.user_id == user_id).first()
    if existing_res:
        old_spot = db.query(ParkingSpot).filter(ParkingSpot.id == existing_res.spot_id).first()
        if old_spot:
            old_spot.status = "free"
        db.delete(existing_res)

    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(404, "Spot not found")
    if spot.status != "free":
        raise HTTPException(409, "Spot is not available")

    spot.status = "reserved"
    reservation = Reservation(user_id=user_id, spot_id=spot_id)
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return {
        "reservation": {
            "id":          reservation.id,
            "spot":        spot_dict(spot),
            "reserved_at": reservation.started_at.isoformat()
        }
    }


@app.delete("/api/reservations/mine")
def cancel_reservation(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    reservation = db.query(Reservation).filter(Reservation.user_id == user_id).first()
    if not reservation:
        raise HTTPException(404, "No active reservation")

    spot = db.query(ParkingSpot).filter(ParkingSpot.id == reservation.spot_id).first()
    now = datetime.datetime.utcnow()

    duration_min = max(1, math.ceil((now - reservation.started_at).total_seconds() / 60))
    rate_num = float(''.join(c for c in spot.rate if c.isdigit() or c == '.'))
    cost = round(rate_num * duration_min / 60, 2)

    # save trip
    trip = Trip(
        user_id      = user_id,
        spot_id      = spot.id,
        label        = spot.floor + spot.row + str(spot.col),
        floor        = spot.floor,
        spot_type    = spot.spot_type,
        ev           = spot.ev,
        rate         = spot.rate,
        duration_min = duration_min,
        cost         = cost,
        started_at   = reservation.started_at,
        ended_at     = now,
    )
    db.add(trip)

    spot.status = "free"
    db.delete(reservation)
    db.commit()
    db.refresh(trip)

    return {"trip": trip_dict(trip)}


# ── History routes ────────────────────────────────────────────────────────────

@app.get("/api/history")
def get_history(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    trips = (
        db.query(Trip)
        .filter(Trip.user_id == user_id)
        .order_by(Trip.ended_at.desc())
        .all()
    )
    return [trip_dict(t) for t in trips]


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}
