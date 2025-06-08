import time
from typing import Any, Dict
import requests
from requests.exceptions import (ConnectionError, Timeout, HTTPError)

from betsapi_football_scraper.infrastructure.config import Settings
from betsapi_football_scraper.infrastructure.logger import logger

class HttpClient:
    """Минимальный HTTP‑клиент без прокси, но с ретраями и задержкой."""

    def __init__(self, cfg: Settings):
        self.cfg = cfg

    def get_json(self, url: str, *, params: Dict[str, Any] | None = None, timeout: int = 10):
        attempts_left = self.cfg.max_retries
        last_exc: Exception | None = None
        while attempts_left:
            try:
                resp = requests.get(url, params=params, timeout=timeout)
                resp.raise_for_status()
                time.sleep(self.cfg.request_delay)
                return resp.json()
            except (ConnectionError, Timeout, HTTPError) as exc:
                last_exc = exc
                logger.warning("Request failed: {} ({} left)", exc, attempts_left - 1)
                attempts_left -= 1
                time.sleep(self.cfg.request_delay)
        raise RuntimeError(f"GET {url} failed") from last_exc