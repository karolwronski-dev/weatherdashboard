import json
import os
import requests

CONFIG_FILE = "user.json"


def get_user_info():
    if not os.path.exists(CONFIG_FILE):
        name = input("Welcome! Before you start, what is your name? ")
        city = input(
            "Where do you live? I want to know which city I have to show by default! ")

        profile = {"name": name, "city": city}

        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(profile, file)

        return True, name, city

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        profile = json.load(file)

        return False, profile["name"], profile["city"]


def get_city_coordinates(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    try:
        response = requests.get(url)
        data = response.json()
        if "results" in data:
            res = data["results"][0]
            return res["latitude"], res["longitude"]
        return None, None
    except Exception:
        return None, None
