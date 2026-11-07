import json
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from db import Database
from rabbit import publisher

BOTS_DIR    = os.environ.get("BOTS_DIR",    "/tmp/bots")
HISTORY_DIR = os.environ.get("HISTORY_DIR", "/tmp/games")

os.makedirs(BOTS_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)
app = FastAPI()
db  = Database()


@app.post("/api/v1/game", status_code=201)
async def create_game(
    bot1: UploadFile,
    bot2: UploadFile,
    seed: int = Form(...),
):
    game_id = str(uuid.uuid4())

    ext1 = Path(bot1.filename or "bot.py").suffix or ".py"
    ext2 = Path(bot2.filename or "bot.py").suffix or ".py"
    bot1_path = os.path.join(BOTS_DIR, f"{game_id}_player1{ext1}")
    bot2_path = os.path.join(BOTS_DIR, f"{game_id}_player2{ext2}")

    with open(bot1_path, "wb") as f:
        f.write(await bot1.read())
    with open(bot2_path, "wb") as f:
        f.write(await bot2.read())

    db.create_game(game_id, seed, bot1_path, bot2_path)

    publisher.publish({
        "game_id":     game_id,
        "seed":        seed,
        "bot1_path":   bot1_path,
        "bot2_path":   bot2_path,
        "retry_count": 0,
    })

    return {"game_id": game_id, "url": f"/api/v1/game/{game_id}"}


@app.get("/api/v1/game/{game_id}")
async def get_game(game_id: str):
    game = db.get_game(game_id)

    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    status = game["status"]

    if status in ("pending", "running"):
        return {"status": status}

    if status == "error":
        return {"status": "error", "error": game["error"]}

    # done — return history JSON
    history_path = game["history_path"]
    if not history_path or not os.path.exists(history_path):
        raise HTTPException(status_code=404, detail="History file not found")

    with open(history_path) as f:
        return json.load(f)
