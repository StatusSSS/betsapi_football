from __future__ import annotations
import time

from betsapi_football_scraper.infrastructure.config import Settings
from betsapi_football_scraper.infrastructure.db import DB
from betsapi_football_scraper.infrastructure.http_client import HttpClient
from betsapi_football_scraper.infrastructure.logger import logger
from betsapi_football_scraper.repositories.teams_repo import TeamsRepo
from betsapi_football_scraper.scraping.scraper import TeamsMarketValueScraper


def main() -> None:
    cfg = Settings()
    db = DB(cfg)
    http = HttpClient(cfg)
    teams_repo = TeamsRepo(db)

    scraper = TeamsMarketValueScraper(
        db=db,
        http=http,
        teams_repo=teams_repo,
        cfg=cfg,
    )

    logger.info("Scraper started")


    try:
        scraper.run_one_cycle()
    except KeyboardInterrupt:
        logger.info("[STOP] interrupted by user")
    except Exception as exc:
        logger.opt(exception=exc).error("Unhandled exception — sleeping {} s", cfg.error_delay)
        time.sleep(cfg.error_delay)
        db.reconnect()


if __name__ == "__main__":
    main()