import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Neon PostgreSQL connection string
# Set DATABASE_URL env variable:

from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False)
    phone       = Column(String, unique=True, index=True, nullable=False)
    plate       = Column(String, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    trips       = relationship("Trip", back_populates="user")
    reservation = relationship("Reservation", back_populates="user", uselist=False)


class ParkingSpot(Base):
    __tablename__ = "parking_spots"
    id        = Column(String, primary_key=True)
    floor     = Column(String(1), nullable=False)
    row       = Column(String(1), nullable=False)
    col       = Column(Integer,   nullable=False)
    status    = Column(String,    default="free")
    ev        = Column(Boolean,   default=False)
    spot_type = Column(String,    default="Standard")
    rate      = Column(String,    default="$2.0/hr")

    reservation = relationship("Reservation", back_populates="spot", uselist=False)


class Reservation(Base):
    __tablename__ = "reservations"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), unique=True)
    spot_id    = Column(String,  ForeignKey("parking_spots.id"), unique=True)
    started_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User",        back_populates="reservation")
    spot = relationship("ParkingSpot", back_populates="reservation")


class Trip(Base):
    __tablename__ = "trips"
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    spot_label   = Column(String)
    floor        = Column(String(1))
    spot_type    = Column(String)
    ev           = Column(Boolean, default=False)
    rate         = Column(String)
    duration_min = Column(Integer)
    cost         = Column(Float)
    ended_at     = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trips")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)