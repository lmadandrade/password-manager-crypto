import json
import os

# storage.py

# This file handles reading from and writing to the vault file

VAULT_PATH = "data/vault.json"


def load_vault():
    # Load the saved vault data from the JSON file
    if not os.path.exists(VAULT_PATH):
        return {"version": 1, "salt": None, "entries": []}

    with open(VAULT_PATH, "r") as file:
        return json.load(file)


def save_vault(vault_data):
    # Save the updated vault data to the JSON file
    with open(VAULT_PATH, "w") as file:
        json.dump(vault_data, file, indent=4)


def reset_vault():
    # Reset the vault back to the empty starting state
    empty_vault = {
        "version": 1,
        "salt": None,
        "entries": []
    }

    # Save the empty vault into the JSON file
    with open(VAULT_PATH, "w") as file:
        json.dump(empty_vault, file, indent=4)