from utils import *
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime


def main():
    is_first_time, user_name, city_name = get_user_info()

    if is_first_time:
        print(f"Nice to meet You, {user_name}! Let me configure dashboard...")
    else:
        print(f"Welcome again, {user_name}! Loading...")

    lat, lon = get_city_coordinates(city_name)

    openmeteo = openmeteo_requests.Client()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
        "current": ["temperature_2m", "relative_humidity_2m"],
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_relative_humidity_2m = current.Variables(1).Value()
    print(f"Current time: {datetime.fromtimestamp(current.Time())}")
    print(f"Current temperature_2m: {current_temperature_2m}")
    print(f"Current relative_humidity_2m: {current_relative_humidity_2m}")


if __name__ == "__main__":
    main()
