import random
from sqlalchemy.orm import Session
from app.database import ParkingSpot

FLOORS = {
    "A": {"rows": ["A","B","C","D"], "cols": 10},
    "B": {"rows": ["A","B","C","D"], "cols": 10},
    "C": {"rows": ["A","B","C"],     "cols": 8},
}
EV_SPOTS = {"A_A1","A_A2","A_D9","A_D10","B_B1","B_C10","C_A7","C_A8"}
TYPES = ["Compact","Standard","Standard","Large"]


def seed_spots(db: Session):
    if db.query(ParkingSpot).count() > 0:
        # Бар споттардың бәрін free-ге қайтарамыз
        db.query(ParkingSpot).update({"status": "free"})
        db.commit()
        return
    spots = []
    for floor, cfg in FLOORS.items():
        for row in cfg["rows"]:
            for col in range(1, cfg["cols"] + 1):
                sid = f"{floor}_{row}{col}"
                spots.append(ParkingSpot(
                    id = sid,
                    floor = floor,
                    row = row,
                    col = col,
                    status = "free",
                    ev = sid in EV_SPOTS,
                    spot_type = random.choice(TYPES),
                    rate = f"${round(1.5 + random.random()*1.5, 1)}/hr",
                ))
    db.bulk_save_objects(spots)
    db.commit()
    print(f"[seed] {len(spots)} spots created")