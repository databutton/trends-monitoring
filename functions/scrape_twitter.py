from config.config import HASHTAG_LIST, TWEET_DATA_KEY
import requests
import pandas as pd
import databutton as db
from datetime import datetime, timedelta, timezone
import re
import sys

sys.path.append(".")


bearer_token = db.secrets.get('TWITTER_BEARER_TOKEN')


def timestamp_start_of_day():
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%dT00:00:00.000Z"), today.strftime("%Y-%m-%dT00:00:00.000Z")


def fetch_tweet_stats(hashtag: str, start_time_utc: str, end_time_utc: str):
    return requests.get(
        f"https://api.twitter.com/2/tweets/counts/recent?query=%22{hashtag}%22&start_time={start_time_utc}&end_time={end_time_utc}",
        headers={"Authorization": f"Bearer {bearer_token}"},
    ).json()


def scrape_twitter(start_time_utc: str, end_time_utc: str):
    df = db.storage.dataframes.get(TWEET_DATA_KEY)

    print(
        f"Fetching tweets from (incl) {start_time_utc} to (excl) {start_time_utc}")
    regex = r"\d{4}-\d{2}-\d{2}"

    for hashtag in HASHTAG_LIST:
        print(f"Fetching stats for hashtag: {hashtag}")
        stats = fetch_tweet_stats(
            hashtag=hashtag, start_time_utc=start_time_utc, end_time_utc=end_time_utc)

        print(stats)

        for item in stats["data"]:
            id = f"{hashtag}-{item['start']}"
            skip_id_check = "id" not in df.columns
            if skip_id_check or not (df["id"] == id).any():
                start_time = item["start"]
                end_time = item["end"]
                print(f"{start_time} -> {end_time}")
                if not re.search(regex, start_time) or not re.search(regex, end_time):
                    print(f"Invalid response: {item}")

                if "1970" in item["start"] or "1970" in item["end"]:
                    print(item)

                else:
                    df = pd.concat(
                        [
                            df,
                            pd.DataFrame(
                                [
                                    {
                                        "id": f"{hashtag}-{item['start']}",
                                        "hashtag": hashtag,
                                        "start_time": start_time,
                                        "end_time": end_time,
                                        "tweet_count": item["tweet_count"],
                                    }
                                ]
                            ),
                        ],
                        ignore_index=True,
                    )
            else:
                print(f"ID: {id} already in dataframe. Skipping")

    # db.storage.dataframes.put(df, TWEET_DATA_KEY)


@db.jobs.repeat_every(seconds=60 * 60 * 12)  # Every twelve hours
def twitter_job():
    start_of_day_utc, end_of_day_utc = timestamp_start_of_day()
    scrape_twitter(start_time_utc=start_of_day_utc,
                   end_time_utc=end_of_day_utc)


if __name__ == "__main__":
    scrape_twitter(
        start_time_utc='2022-08-01T00:00:00.000Z',
        end_time_utc='2022-08-02T00:00:00.000Z'
    )
