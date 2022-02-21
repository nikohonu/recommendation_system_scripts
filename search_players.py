from math import ulp
import requests
import random
import json
import time
import nh_tools.file
import pathlib

#start = 76561197960265729
start = 76561198083927294 - 1
end = 76561198899999999
steam_id = start
steam_ids = nh_tools.file.open_json(pathlib.Path('users.json'), [])
steam_ids = set(steam_ids)
while len(steam_ids) < 100:
    steam_id += 1
    #steam_id = random.randrange(start, end)
    time.sleep(4)
    try:
        url = f"http://127.0.0.1:5000/get-playtime/{steam_id}"
        print(url, len(steam_ids))
        result = requests.get(url)
        result = result.json()
        steam_ids.add(steam_id)
        print('ok')
    except json.decoder.JSONDecodeError:
        continue
print(steam_ids)
nh_tools.file.save_json(pathlib.Path('users.json'), list(steam_ids))
