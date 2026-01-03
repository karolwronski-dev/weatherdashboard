import json
import os
import requests
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime

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


def connect():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    return openmeteo


def fetch_forecast(openmeteo, lat, lon):
    if lat is None or lon is None:
        return None

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
        "current": ["temperature_2m"],
    }

    responses = openmeteo.weather_api(url, params=params)
    return responses[0]


def display_city_weather(city, response):
    if response is None:
        print(f"Could not get data for {city}")
        return

    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()

    print(f"\nDashboard for: {city}")
    print(f"Current time: {datetime.fromtimestamp(current.Time())}")
    print(f"Current temperature: {round(current_temperature_2m)}°C")

    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}

    hourly_data["temperature"] = hourly_temperature_2m
    hourly_df = pd.DataFrame(data=hourly_data)

    today = pd.Timestamp.now(tz='UTC').normalize()

    hourly_df = hourly_df[hourly_df['date'].dt.normalize() == today].copy()
    hourly_df['date'] = hourly_df['date'].dt.strftime("  %H:%M  ")

    hourly_df = hourly_df.set_index("date")
    hourly_df.index.name = today.strftime("%d %b")
    hourly_df['temperature'] = hourly_df['temperature'].apply(
        lambda x: f"{x:.1f}°C")

    hourly_df = hourly_df.T

    print("\n", hourly_df)


def start():
    is_first_time, user_name, main_city = get_user_info()
    is_running = True

    if is_first_time:
        print(f"Nice to meet You, {user_name}! Let me configure dashboard...")
    else:
        print(f"Welcome again, {user_name}! Loading...")

    openmeteo = connect()

    lat, lon = get_city_coordinates(main_city)
    response = fetch_forecast(openmeteo, lat, lon)
    display_city_weather(main_city, response)

    while (is_running):
        another_city = input(f"{user_name}, write another city or leave (q): ")
        if (another_city == "q"):
            is_running = False
            break
        else:
            lat, lon = get_city_coordinates(another_city)
            if (lat != None and lon != None):
                response = fetch_forecast(openmeteo, lat, lon)
                display_city_weather(another_city, response)
            else:
                print(f"Cant find city: {another_city}")


if __name__ == "__main__":
    start()
