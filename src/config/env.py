import os
from pathlib import Path


def load_env(env_path: Path) -> None:

    if not env_path.exists():
        return

    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()


def get_bool_env(key: str, default: bool = False) -> bool:

    value = os.getenv(key)

    if value is None:
        return default

    return value.lower() in {"1", "true", "yes", "on"}
