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
    print(f"Current temperature: {current_temperature_2m}")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}

    hourly_data['date'] = hourly_data['date'].strftime(
        "%d %b, %H:%M")
    hourly_data["temperature"] = hourly_temperature_2m
    hourly_dataframe = pd.DataFrame(data=hourly_data)

    print(f"\nDashboard for: {city_name}\n\n", hourly_dataframe)


if __name__ == "__main__":
    main()
