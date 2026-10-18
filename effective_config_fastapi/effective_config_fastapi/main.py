
import os
from pathlib import Path

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def normalize_layer(layer):
    result = {}

    for key, value in (layer or {}).items():
        if value is None:
            continue

        key = str(key).strip()

        if key.upper() == "NUM_WORKERS":
            key = "workers"
        elif key.upper().startswith("APP_"):
            key = key[4:].lower()
        else:
            key = key.lower()

        result[key] = value

    return result


def to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def coerce(key, value):
    if key in {"port", "workers"}:
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)


def get_effective_config(overrides):
    config = dict(DEFAULTS)

    # 1. YAML configuration
    env_name = os.environ.get("APP_ENV", "development")
    yaml_path = BASE_DIR / f"config.{env_name}.yaml"

    if yaml_path.exists():
        with yaml_path.open("r", encoding="utf-8") as f:
            config.update(normalize_layer(yaml.safe_load(f)))

    # 2. .env configuration
    config.update(normalize_layer(dotenv_values(BASE_DIR / ".env")))

    # 3. Operating-system environment variables
    os_layer = {
        key: value
        for key, value in os.environ.items()
        if key.startswith("APP_") and key != "APP_ENV"
    }

    if "NUM_WORKERS" in os.environ:
        os_layer["NUM_WORKERS"] = os.environ["NUM_WORKERS"]

    config.update(normalize_layer(os_layer))

    # 4. Query-string overrides have highest precedence
    for item in overrides:
        if "=" not in item:
            continue

        key, value = item.split("=", 1)
        key = key.strip().lower()

        if key == "num_workers":
            key = "workers"

        if key.startswith("app_"):
            key = key[4:]

        if key:
            config[key] = value

    # Convert values to the required types
    for key in ("port", "workers"):
        config[key] = int(config[key])

    config["debug"] = to_bool(config["debug"])
    config["log_level"] = str(config["log_level"])

    # Never reveal the actual API key
    config["api_key"] = "****"

    return config


app = FastAPI(title="Effective Configuration Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "endpoint": "/effective-config"}


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    return get_effective_config(set)
