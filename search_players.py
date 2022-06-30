'''Script for getting player steam id with public game list and save it to
user.json'''
import json
import pathlib
import random
import time

import nh_tools.file
import requests

START = 76561198083927293
END = 76561198899999999
steam_ids = nh_tools.file.open_json(pathlib.Path('steam_ids.json'), [])
steam_ids = set(steam_ids)
while len(steam_ids) < 1000:
    steam_id = random.randrange(START, END)
    time.sleep(4)
    try:
        url = f"http://127.0.0.1:5000/get-playtime/{steam_id}"
        print(url, len(steam_ids))
        result = requests.get(url)
        result = result.json()
        steam_ids.add(steam_id)
        nh_tools.file.save_json(pathlib.Path(
            'steam_ids.json'), list(steam_ids))
        print('ok')
    except json.decoder.JSONDecodeError:
        continue
