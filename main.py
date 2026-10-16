from typing import List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: lets the grader's web page call your API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- The four layers (lowest to highest precedence) ----
DEFAULTS = {
    "port": "8000", "workers": "1", "debug": "false",
    "log_level": "info", "api_key": "default-secret-000",
}
YAML_DEV = {"port": "8151", "debug": "true", "log_level": "error"}
DOTENV = {"APP_PORT": "8070", "NUM_WORKERS": "15", "APP_LOG_LEVEL": "debug"}
OS_ENV = {"APP_PORT": "8585", "APP_WORKERS": "4", "APP_DEBUG": "false"}

ALIASES = {"num_workers": "workers"}


def normalize(layer: dict) -> dict:
    """Turn APP_PORT -> port, NUM_WORKERS -> workers, etc."""
    out = {}
    for key, value in layer.items():
        k = key.lower()
        if k.startswith("app_"):
            k = k[4:]
        k = ALIASES.get(k, k)
        out[k] = value
    return out


def to_bool(v) -> bool:
    return str(v).strip().lower() in ("true", "1", "yes", "on")


def coerce(cfg: dict) -> dict:
    out = {}
    for k, v in cfg.items():
        if k in ("port", "workers"):
            out[k] = int(v)
        elif k == "debug":
            out[k] = to_bool(v)
        else:
            out[k] = str(v)
    return out


@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):
    cfg = {}
    # Later updates overwrite earlier ones = higher precedence
    for layer in (DEFAULTS, YAML_DEV, normalize(DOTENV), normalize(OS_ENV)):
        cfg.update(layer)

    # CLI overrides: "port=9000" -> split on the FIRST "=" only
    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            cfg[key.strip().lower()] = value.strip()

    cfg = coerce(cfg)
    cfg["api_key"] = "****"  # always masked, even if overridden
    return cfg