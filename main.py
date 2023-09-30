# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import spotify_client
from sqlalchemy import Table, Column, Integer, String, MetaData
import sqlalchemy
import pandas as pd
import datetime
import sqlite3
import datetime

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"


def check_if_valid_data(df: pd.DataFrame) -> bool:
    # Check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False

    # Primary Key Check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key check is violated")

    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null values found")

    # Check that all timestamps are in the last 24hrs
    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.fromisoformat(timestamp[:-1]).timestamp() < timestamp_24h_earlier:
            raise Exception(")At least one of the returned songs does not have a yesterday's timestamp")

    return True


at_24h_earlier = datetime.datetime.today() - datetime.timedelta(days=1)
timestamp_24h_earlier = int(at_24h_earlier.timestamp())
last_played_songs = spotify_client.get_last_played_songs(after=timestamp_24h_earlier)

song_names = []
artist_names = []
played_at_list = []
timestamps = []

for song in last_played_songs["items"]:
    if datetime.datetime.fromisoformat(song["played_at"][:-1]).timestamp() >= timestamp_24h_earlier:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"])

song_dict = {
    "song_name": song_names,
    "artist_name": artist_names,
    "played_at": played_at_list,
    "timestamp": timestamps
}

song_df = pd.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])
if check_if_valid_data(song_df):
    print("Data valid, proceed to Load stage")

engine = sqlalchemy.create_engine(DATABASE_LOCATION)
conn = sqlite3.connect('my_played_tracks.sqlite')
cursor = conn.cursor()

meta = MetaData()

my_taste_in_music = Table(
'songs', meta,
Column('played_at', Integer, primary_key = True),
Column('name', String),
Column('artists', String),
Column('timestamp', String),
)
print(my_taste_in_music)
print("Opened databse successfully")

try:
    song_df.to_sql("my_taste_in_music", engine, index=False, if_exists='append')
except :
    print("Data already exists in the database")

conn.close()
print("Close database successfully")