import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/botfleet")


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True

    def create_game(self, game_id: str, seed: int, bot1_path: str, bot2_path: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO games (id, status, seed, bot1_path, bot2_path, created_at, updated_at)
                VALUES (%s, 'pending', %s, %s, %s, NOW(), NOW())
                """,
                (game_id, seed, bot1_path, bot2_path),
            )

    def get_game(self, game_id: str) -> dict | None:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, status, history_path, winner, error FROM games WHERE id = %s",
                (game_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
