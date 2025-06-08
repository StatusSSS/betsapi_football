import pymysql.cursors
from contextlib import contextmanager
from typing import Iterator, Any
from betsapi_football_scraper.infrastructure.config import Settings
from betsapi_football_scraper.infrastructure.logger import logger

class DB:
    def __init__(self, cfg: Settings):
        self.cfg = cfg
        self._connect()

    def _connect(self) -> None:
        self.conn = pymysql.connect(
            host=self.cfg.db_host,
            port=self.cfg.db_port,
            user=self.cfg.db_user,
            passwd=self.cfg.db_pass,
            db=self.cfg.db_name,
            ssl_ca=self.cfg.db_ssl_ca,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
        self.cur = self.conn.cursor()
        logger.info(
            "DB connected → {}:{} / {}",
            self.cfg.db_host, self.cfg.db_port, self.cfg.db_name
        )

    def reconnect(self) -> None:
        try:
            self.conn.ping(reconnect=True)
        except Exception:
            logger.warning("Re-connecting DB…")
            self._connect()

    @contextmanager
    def transaction(self) -> Iterator[Any]:
        try:
            yield self.cur
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def close(self) -> None:
        self.cur.close()
        self.conn.close()
