from typing import List, Dict, Tuple
from betsapi_football_scraper.infrastructure.logger import logger


class TeamsRepo:
    def __init__(self, db):
        self.db = db

    def all(self) -> List[Dict]:
        sql = (
            "SELECT id, common_title, betsapi_id, total_market_value, avg_market_value, "
            "avg_age, natioanal_team_players, foreigners "
            "FROM teams WHERE betsapi_id IS NOT NULL ORDER BY id;"
        )
        self.db.reconnect()
        self.db.cur.execute(sql)
        return self.db.cur.fetchall()


    def bulk_update_market(self, rows: List[Tuple]) -> None:
        """Обновляет БД сразу пачкой"""
        if not rows:
            return

        sql = (
            "UPDATE teams "
            "SET total_market_value=%s, avg_market_value=%s, foreigners=%s, "
            "natioanal_team_players=%s, avg_age=%s, updated_at=NOW() "
            "WHERE id=%s;"
        )


        with self.db.transaction() as cur:
            cur.executemany(sql, rows)

        logger.debug("bulk_update_market: committed {} rows", len(rows))
