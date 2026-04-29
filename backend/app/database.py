from sqlalchemy import (
    create_engine, Column, String, Boolean,
    Integer, Float, DateTime, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./parking.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    phone      = Column(String, unique=True, index=True, nullable=False)
    plate      = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id        = Column(String, primary_key=True)   # e.g. "A_A1"
    floor     = Column(String, nullable=False)
    row       = Column(String, nullable=False)
    col       = Column(Integer, nullable=False)
    status    = Column(String, default="free")      # free | occupied | reserved
    ev        = Column(Boolean, default=False)
    spot_type = Column(String, nullable=False)
    rate      = Column(String, nullable=False)


class Reservation(Base):
    __tablename__ = "reservations"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    spot_id    = Column(String,  ForeignKey("parking_spots.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)


class Trip(Base):
    __tablename__ = "trips"

    id           = Column(Integer, primary_key=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    spot_id      = Column(String,  nullable=False)
    label        = Column(String,  nullable=False)
    floor        = Column(String,  nullable=False)
    spot_type    = Column(String,  nullable=False)
    ev           = Column(Boolean, default=False)
    rate         = Column(String,  nullable=False)
    duration_min = Column(Integer, nullable=False)
    cost         = Column(Float,   nullable=False)
    started_at   = Column(DateTime, nullable=False)
    ended_at     = Column(DateTime, default=datetime.datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
