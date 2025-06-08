import time
from typing import Dict, List, Tuple
from tqdm import tqdm

from betsapi_football_scraper.infrastructure.config import Settings
from betsapi_football_scraper.infrastructure.http_client import HttpClient
from betsapi_football_scraper.infrastructure.logger import logger
from betsapi_football_scraper.repositories.teams_repo import TeamsRepo


class TeamsMarketValueScraper:

    BASE_V3 = "https://api.b365api.com/v3"
    BASE_V1 = "https://api.betsapi.com/v1"

    def __init__(self, *, db, http: HttpClient, teams_repo: TeamsRepo, cfg: Settings):
        self.db = db
        self.http = http
        self.teams_repo = teams_repo
        self.cfg = cfg


    def run_one_cycle(self) -> None:
        teams = self.teams_repo.all()
        logger.info("Fetched {} teams", len(teams))

        update_rows: List[Tuple] = []
        processed_in_batch = 0

        for team in tqdm(teams, desc="teams"):
            try:
                self._process_team_flow(team, update_rows)
            except Exception as exc:
                logger.opt(exception=exc).warning("Error processing team {}", team["id"])

            processed_in_batch += 1
            if processed_in_batch == self.cfg.batch_size:
                self.teams_repo.bulk_update_market(update_rows)
                update_rows.clear()
                processed_in_batch = 0

        if update_rows:
            self.teams_repo.bulk_update_market(update_rows)


    def _process_team_flow(self, team: Dict, update_rows: List[Tuple]) -> None:
        """qwe"""
        match_id_upcoming = self._closest_match(team["betsapi_id"], "upcoming")

        stats_tuple = None
        if match_id_upcoming:
            stats_tuple = self._process_match(team, match_id_upcoming)
        if stats_tuple is None:
            match_id_ended = self._closest_match(team["betsapi_id"], "ended")
            if match_id_ended:
                stats_tuple = self._process_match(team, match_id_ended)
        if stats_tuple is None:
            return

        total_mv, avg_mv, foreigners, nt_players, avg_age = stats_tuple


        if (
            str(team["total_market_value"]) == str(total_mv)
            and str(team["avg_market_value"]) == str(avg_mv)
            and str(team["foreigners"]) == str(foreigners)
            and str(team["natioanal_team_players"]) == str(nt_players)
            and str(team["avg_age"]) == str(avg_age)
        ):
            return

        update_rows.append((*stats_tuple, team["id"]))



    def _closest_match(self, team_id: int, mode: str) -> int | None:
        url = f"{self.BASE_V3}/events/{mode}"
        data = self.http.get_json(
            url,
            params={
                "sport_id": self.cfg.sport_id,
                "team_id": team_id,
                "token": self.cfg.betsapi_token,
            },
        )
        results = data.get("results", [])
        return results[0]["id"] if results else None

    def _event_details(self, event_id: int) -> Dict:
        url = f"{self.BASE_V1}/event/view"
        data = self.http.get_json(
            url,
            params={
                "event_id": event_id,
                "get_tm": 1,
                "token": self.cfg.betsapi_token,
            },
        )
        return data.get("results", [{}])[0] if data.get("results") else {}

    def _process_match(self, team: Dict, match_id: int) -> Tuple | None:
        details: Dict | None = None
        for _ in range(10):
            details = self._event_details(match_id)
            if details:
                break
            time.sleep(self.cfg.request_delay)

        if not details:
            return None

        if team["betsapi_id"] == int(details["home"]["id"]):
            idx = 0
        elif team["betsapi_id"] == int(details["away"]["id"]):
            idx = 1
        else:
            return None


        if str(match_id) == "9834789":
            idx = 1 - idx

        tm = details.get("tm_stats", {})
        new_vals = {
            "total_market_value": tm.get("total_market_value", [None, None])[idx],
            "avg_market_value": tm.get("avg_market_value", [None, None])[idx],
            "foreigners": tm.get("foreigners", [None, None])[idx],
            "natioanal_team_players": tm.get("national_team_players", [None, None])[idx],
            "avg_age": tm.get("avg_age", [None, None])[idx],
        }

        if all(v is None for v in new_vals.values()):
            return None

        try:
            for val in new_vals.values():
                if val is not None:
                    float(val)
        except (TypeError, ValueError):
            return None

        return (
            new_vals["total_market_value"],
            new_vals["avg_market_value"],
            new_vals["foreigners"],
            new_vals["natioanal_team_players"],
            new_vals["avg_age"],
        )