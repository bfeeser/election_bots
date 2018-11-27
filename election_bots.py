from configparser import ConfigParser
from csv import DictReader, DictWriter
import click
from datetime import date
import os
from urllib.parse import urlencode


import twitter


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


def read_config(path="config"):
    if os.path.exists(path):
        config = ConfigParser()
        config.read(path)
        return config
    raise RuntimeError(f"Missing {path} config file")


def get_twitter_api():
    config = read_config()

    return twitter.Api(
        consumer_key=config.get("twitter", "consumer_key"),
        consumer_secret=config.get("twitter", "consumer_secret"),
        access_token_key=config.get("twitter", "access_token_key"),
        access_token_secret=config.get("twitter", "access_token_secret"),
        sleep_on_rate_limit=True,
    )


def get_user_ids_from_csv(file):
    with open(file) as csvfile:
        user_ids = [row["user_id"] for row in DictReader(csvfile)]
    return user_ids


def write_tweets_to_csv(writer, tweets):
    for tweet in tweets:
        writer.writerow(
            {
                "user_id": tweet.id,
                "screen_name": tweet.user.screen_name,
                "text": tweet.text,
                "timestamp": tweet.created_at,
            }
        )


@click.group()
def cli():
    pass


@cli.command()
@click.argument("output")
@click.option("--query", "-q", multiple=True, default=HASHTAGS)
@click.option("--since", "-s", default="2018-09-01")
@click.option("--until", "-u", default="2018-11-20")
@click.option("--count", "-c", default=100, help="Number of tweets to pull")
def search(output, query, since, until, count):
    "OUTPUT: CSV file with tweets that match a query, such as a hashtag."

    api = get_twitter_api()

    with open(output, "w") as outfile:
        fieldnames = "user_id", "screen_name", "tweet", "timestamp"
        writer = DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for q in query:
            raw_query = urlencode(
                {"q": q, "since": since, "until": until, "count": count}
            )

            tweets = api.GetSearch(raw_query=raw_query)
            write_tweets_to_csv(writer, tweets)


@cli.command()
@click.argument("input")
@click.argument("output")
def followers(input, output):
    """INPUT: CSV file containing user_ids
       OUTPUT: CSV file with followers and followee user_ids"""

    api = get_twitter_api()

    with open(output, "w") as outfile:
        fieldnames = "follwer", "followee"
        writer = DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for followee in get_user_ids_from_csv(input):
            for follower in api.GetFollowerIDs(followee):
                writer.writerow({"follower": follower, "followee": followee})


@cli.command()
@click.argument("input")
@click.argument("output")
def timeline(input, output):
    """INPUT: CSV file containing user_ids
       OUTPUT: CSV file with users' tweet timelines"""

    api = get_twitter_api()

    with open(output, "w") as outfile:
        fieldnames = "user_id", "screen_name", "text", "timestamp"
        writer = DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for user_id in get_user_ids_from_csv(input):
            tweets = GetUserTimeline(user_id)
            write_tweets_to_csv(writer, tweets)


if __name__ == "__main__":
    cli()
