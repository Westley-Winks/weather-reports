import pandas as pd
import json
import openmeteo_requests
from retry_requests import retry
import requests_cache
from dotenv import load_dotenv
load_dotenv()

VOLUNTEER_DATA_FILE = "data/volunteers.json"
RAW_WEATHER_DATA_FILE = "data/meteo_dataframe.csv"


def read_volunteer_data(file: str) -> list:
    """
        Converts the json data to a list of dictionaries. Each dictionary is
        data for a different volunteer.
    """
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()

    data = json.loads(content)
    return data


def fetch_data(data: dict, start_date: str, end_date: str) -> pd.DataFrame:
    """
        Calls the open-meteo api and puts it into a pandas dataframe
    """
    # Most of this code is from the open-meteo docs
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": {data['lat']},
        "longitude": {data['lon']},
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "rain_sum",
            "wind_speed_10m_max",
            "wind_gusts_10m_max"],
        "timezone": "Europe/London",
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]

    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_mean = daily.Variables(2).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(3).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(4).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(5).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(6).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(7).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(8).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s"),
        end=pd.to_datetime(daily.TimeEnd(), unit="s"),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )}
    daily_data["volunteer_name"] = data["volunteer_name"]
    daily_data["site_name"] = data["site_name"]
    daily_data["temp_max_C"] = daily_temperature_2m_max
    daily_data["temp_min_C"] = daily_temperature_2m_min
    daily_data["temp_mean_C"] = daily_temperature_2m_mean
    daily_data["apparent_temp_max_C"] = daily_apparent_temperature_max
    daily_data["apparent_temp_min_C"] = daily_apparent_temperature_min
    daily_data["precipitation_sum_mm"] = daily_precipitation_sum
    daily_data["rain_sum_mm"] = daily_rain_sum
    daily_data["wind_speed_10m_max_kmh"] = daily_wind_speed_10m_max
    daily_data["wind_gusts_10m_max_kmh"] = daily_wind_gusts_10m_max

    daily_dataframe = pd.DataFrame(data=daily_data)

    return daily_dataframe


def save_data(df, save_file):
    """
        This saves the data into a csv file for further exploration in Jupyter.
        The data file gets overwritten each time so only the previous weeks
        data is saved.
    """
    column_order = [
        "date",
        "volunteer_name",
        "site_name",
        "temp_max_C",
        "temp_min_C",
        "temp_mean_C",
        "apparent_temp_max_C",
        "apparent_temp_min_C",
        "precipitation_sum_mm",
        "rain_sum_mm",
        "wind_speed_10m_max_kmh",
        "wind_gusts_10m_max_kmh"
    ]

    df[column_order].to_csv(save_file, mode="w", header=True)
    print(f"Complete. Data saved in {save_file}")


def C_to_F(s):
    s_F = s * (9/5) + 32
    return s_F


def add_F_values(df):
    """
        Add in standard units alongside the metric
    """

    temp_cols = [
        "temp_max",
        "temp_min",
        "temp_mean",
        "apparent_temp_max",
        "apparent_temp_min",
    ]

    for col in temp_cols:
        df[col+"_F"] = df[col+"_C"].apply(C_to_F)

    return df


def get_data(start_date, end_date) -> pd.DataFrame:
    volunteer_data = read_volunteer_data(VOLUNTEER_DATA_FILE)['data']

    volunteer_frames = []
    for volunteer in volunteer_data:
        volunteer_df = fetch_data(volunteer, start_date, end_date)
        volunteer_frames.append(volunteer_df)

    df = pd.concat(volunteer_frames)

    save_data(df, RAW_WEATHER_DATA_FILE)

    df = add_F_values(df)

    return df
