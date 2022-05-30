import databutton as db
import streamlit as st
import pandas as pd

from lib.config import HASHTAG_LIST, TWEET_DATA_KEY


@db.apps.streamlit("/trends", name="Tech Trends")
def trends():
    st.set_page_config(
        page_title="Tech Trends",
        page_icon="📈",
        layout="wide",
    )

    df = db.storage.dataframes.get(TWEET_DATA_KEY)

    for hashtag in HASHTAG_LIST:
        hashtag_df = df[(df["start_time"] > "2022-05-01") & (df["hashtag"] == hashtag)]

        graphed_df = pd.DataFrame(
            {"Date": hashtag_df["start_time"].to_list(), "Value": hashtag_df["tweet_count"].to_list()}
        )
        graphed_df = graphed_df.resample("h", on="Date").Value.sum()

        st.subheader(f"Tweet count: #{hashtag}")
        st.line_chart(graphed_df)
