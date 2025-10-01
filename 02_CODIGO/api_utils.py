import requests
import yaml
import os
import json
from datetime import datetime

def load_config():
    with open("05_CONFIGURACION/config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()

def get_fixtures(league_id):
    cache_file = f"03_DATOS/cache/fixtures_{league_id}.json"
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)
    url = f"{config['api']['base_url_football']}fixtures?league={league_id}&next=20"
    headers = {"X-RapidAPI-Key": config['api']['football_key']}
    response = requests.get(url, headers=headers)
    data = response.json().get('response', [])
    with open(cache_file, "w") as f:
        json.dump(data, f)
    return data
