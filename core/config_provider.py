import json
from pathlib import Path


import os
from dotenv import load_dotenv

class EndpointConfigProvider:

    def __init__(self, config_path: str = None):
        if config_path is None:
            # Obtener la ruta absoluta a la raíz del proyecto
            base_dir = Path(__file__).resolve().parent.parent.parent
            config_path = base_dir / "config" / "endpoints_config.json"
        else:
            config_path = Path(config_path)
        self._config = self._load_config(config_path)

    def _load_config(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, *keys, default=None):
        # Ejemplo: get('BigCommerce', 'GetAllBrands', 'url')
        cfg = self._config
        for key in keys:
            cfg = cfg.get(key, {})
        return cfg or default

# Cargar variables de entorno desde .env
load_dotenv()

def get_mongo_uri():
    user = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASS")
    host = os.getenv("MONGO_HOST")
    port = os.getenv("MONGO_PORT")
    dbname = os.getenv("MONGO_DBNAME")
    if user and password:
        return f"mongodb://{user}:{password}@{host}:{port}/{dbname}"
    else:
        return f"mongodb://{host}:{port}/{dbname}"

# Uso:
# config = EndpointConfigProvider()
# url = config.get('BigCommerce', 'GetAllBrands', 'url')