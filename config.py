import os
import json
from typing import TypedDict, Optional

class Config(TypedDict, total=False):
    base_dir: str

def get_base_dir() -> str:
    config_file = 'config.json'

    if os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            data: Optional[Config] = json.load(f)
            if data is not None and 'base_dir' in data and os.path.isdir(data['base_dir']):
                return data['base_dir']

    while True:
        base_dir = input('Please enter the pokeemerald base directory: ')
        if os.path.isdir(base_dir):
            with open(config_file, 'w') as f:
                json.dump({'base_dir': base_dir}, f)
            return base_dir
        else:
            print(f'"{base_dir}" is not a valid directory. Please try again.')