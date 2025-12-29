import json
import os

CONFIG_FILE = "user.json"


def get_user_info():
    if not os.path.exists(CONFIG_FILE):
        name = input("Welcome! Before you start, what is your name? ")
        city = input(
            "Where do you live? I want to know which city I have to show by default! ")

        profile = {"name": name, "city": city}

        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(profile, file)

        return True, name

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        profile = json.load(file)

        return False, profile["name"]
