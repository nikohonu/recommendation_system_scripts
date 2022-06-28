'''Generate table based on players' data'''
import json
from pathlib import Path

import requests


def main():
    '''Entry point of the script'''
    users = []
    with Path("users.json").open(encoding="UTF-8") as source:
        users = json.load(source)
    for steam_id in users:
        try:
            url = f"http://127.0.0.1:5000/get-playtime/{steam_id}"
            result = requests.get(url)
            result = result.json()
        except requests.exceptions.JSONDecodeError:
            print(steam_id)


if __name__ == '__main__':
    main()
