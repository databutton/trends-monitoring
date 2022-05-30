import sys

sys.path.append(".")

import databutton as db
import pandas as pd
from lib.config import TWEET_DATA_KEY


def main():
    df = pd.DataFrame(data=None).reset_index()
    db.storage.dataframes.put(df, TWEET_DATA_KEY)


if __name__ == "__main__":
    main()
