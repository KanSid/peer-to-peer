import json 
import os
import uuid

CHUNK_SIZE = 4096
SHARED_DIR = "shared"
DOWNLOAD_DIR = "downloads"
TCP_PORT = 5000
DISCOVERY_PORT = 5001

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    return None

def save_config(device_id, name):
    config = {
        "device_id" : device_id,
        "name" : name
    }
    with open(CONFIG_FILE, "w")as f:
        json.dump(config, f, indent=4)
    return config

def get_or_create_config(name=None):
    config = load_config()
    if config:
        return config
    device_id = str(uuid.uuid4())
    return save_config(device_id, name)

def update_name(new_name):
    config = load_config()
    if config:
        config["name"] = new_name
        save_config(config["device_id"], new_name)
