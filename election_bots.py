from configparser import ConfigParser
from datetime import date
import os
from urllib.parse import urlencode
from pprint import pprint

import twitter


def read_config(path="config"):
    if os.path.exists(path):
        config = ConfigParser()
        config.read(path)
        return config
    raise RuntimeError(f"Missing {path} config file")


HASHTAGS = [
    "#gillum",
    "#andrewgillum",
    "#desantis",
    "#rondesantis",
    "#rickscott",
    "#scott",
    "#nelson",
    "#billnelson",
    "#floridaelection",
    "#floridapolitcs",
    "#2018midterms",
    "#flsenate",
    "#flgubernatorial",
]


def main():

    config = read_config()

    api = twitter.Api(
        consumer_key=config.get("twitter", "consumer_key"),
        consumer_secret=config.get("twitter", "consumer_secret"),
        access_token_key=config.get("twitter", "access_token_key"),
        access_token_secret=config.get("twitter", "access_token_secret"),
        sleep_on_rate_limit=True,
    )

    since = date(year=2018, month=8, day=1)
    tweets = []
    count = 100
    for hashtag in HASHTAGS:
        raw_query = urlencode({"q": hashtag, "since": since, "count": count})

        results = api.GetSearch(raw_query=raw_query)

        pprint(results)


if __name__ == "__main__":
    main()
