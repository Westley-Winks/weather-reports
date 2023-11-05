import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
VOLUNTEER_DATA_FILE = "data/volunteers.json"
RAW_WEATHER_DATA_FILE = "data/dataframe.csv"


def read_volunteer_data(file: str) -> pd.DataFrame:
    """
      Converts the json data to a pandas dataframe
    """
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()

    data = json.loads(content)
    raw_df = pd.json_normalize(data["data"])
    return raw_df


def fetch_data(df: pd.DataFrame, date: str) -> pd.DataFrame:
    """
        Calls the openweather api and puts it into a pandas dataframe
    """
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/3.0/onecall/day_summary?"
            f"lat={df['lat']}&"
            f"lon={df['lon']}&"
            f"date={date}&"
            f"units=metric&"
            f"appid={API_KEY}"
        )

        r.raise_for_status()

        data = r.json()

        df["date"] = data["date"]
        df["temp_max_C"] = data["temperature"]["max"]
        df["temp_min_C"] = data["temperature"]["min"]
        df["temp_afternoon_C"] = data["temperature"]["afternoon"]
        df["temp_night_C"] = data["temperature"]["night"]
        df["temp_evening_C"] = data["temperature"]["evening"]
        df["temp_morning_C"] = data["temperature"]["morning"]
        df["wind_max_speed_mps"] = data["wind"]["max"]["speed"]
        df["precipitation_mm"] = data["precipitation"]["total"]
    except:  # TODO; add better error handling
        print(f"Problem detected: {df.index, date}")
    return df


def save_data(df, save_file):
    df.to_csv(save_file, mode="a", header=False)
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
        "temp_afternoon",
        "temp_night",
        "temp_evening",
        "temp_morning"
    ]

    for col in temp_cols:
        df[col+"_F"] = df[col+"_C"].apply(C_to_F)

    return df


def get_data(dates: list) -> pd.DataFrame:
    raw_df = read_volunteer_data(VOLUNTEER_DATA_FILE)

    # Loop through the volunteer dataframe and call the api rowwise
    first = True
    for date in dates:
        date = str(date)
        if first:
            df = raw_df.apply(fetch_data, date=date, axis=1)
        else:
            df = pd.concat([df, raw_df.apply(fetch_data, date=date, axis=1)])
        first = False

    save_data(df, RAW_WEATHER_DATA_FILE)

    df = add_F_values(df)

    return df
