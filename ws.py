import asyncio
import json
import random
from fastapi import WebSocket, WebSocketDisconnect

FLOORS = {
    "A": {"rows": list("ABCD"), "cols": 10},
    "B": {"rows": list("ABCD"), "cols": 10},
    "C": {"rows": list("ABC"),  "cols": 8},
}
PLATES = ["001 NQZ 01","002 ALA 02","004 AKX 04","005 ALA 05","111 KZO 11"]


class WSManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = WSManager()


async def simulator():
    while True:
        await asyncio.sleep(4)
        try:
            floor = random.choice(list(FLOORS.keys()))
            cfg   = FLOORS[floor]
            row   = random.choice(cfg["rows"])
            col   = random.randint(1, cfg["cols"])
            spot_id  = f"{floor}_{row}{col}"
            entering = random.random() > 0.45
            await manager.broadcast({
                "type":    "spot_update",
                "spot_id": spot_id,
                "floor":   floor,
                "status":  "occupied" if entering else "free",
                "plate":   random.choice(PLATES),
                "action":  "entered" if entering else "left",
            })
        except Exception:
            pass
