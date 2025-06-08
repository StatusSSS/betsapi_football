from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:

    db_host: str = os.getenv("DB_HOST")
    db_port: int = int(os.getenv("DB_PORT", 3306))
    db_user: str = os.getenv("DB_USER")
    db_pass: str = os.getenv("DB_PASS")
    db_name: str = os.getenv("DB_NAME")
    db_ssl_ca: str | None = os.getenv("DB_SSL_CA")


    betsapi_token: str = os.getenv("BETSAPI_TOKEN", "27186-iS1mi8evompdHW")
    sport_id: int = 1

    max_retries: int = 5
    request_delay: float = 0.1
    error_delay: int = 30
    batch_size: int = 500
