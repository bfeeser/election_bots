from configparser import ConfigParser
from csv import DictReader, DictWriter
import click
from datetime import date
import os
from random import sample
import tweepy


from hashtags import HASHTAGS


def read_config(path="config"):
    if os.path.exists(path):
        config = ConfigParser()
        config.read(path)
        return config
    raise RuntimeError(f"Missing {path} config file")


def get_twitter_api():
    config = read_config()

    auth = tweepy.OAuthHandler(
        config.get("twitter", "consumer_key"),
        config.get("twitter", "consumer_secret"),
    )

    auth.set_access_token(
        config.get("twitter", "access_token_key"),
        config.get("twitter", "access_token_secret"),
    )

    return tweepy.API(auth, wait_on_rate_limit=True)


def get_column_from_csv(file, column):
    with open(file) as csvfile:
        values = {row[column] for row in DictReader(csvfile)}
    return values


def write_tweet_to_csv(writer, tweet):
    writer.writerow(
        {
            "id": tweet.id,
            "user_id": tweet.user.id,
            "screen_name": tweet.user.screen_name,
            "text": tweet.full_text,
            "created_at": tweet.created_at,
        }
    )


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    "search_type", type=click.Choice(["democratic", "republican", "florida"])
)
@click.option("--since", "-s", default="2018-10-01")
@click.option("--until", "-u", default="2018-11-20")
@click.option("--count", "-c", default=1000, help="Number of tweets to pull")
def search(search_type, since, until, count):
    "OUTPUT: CSV file with tweets that match a query, such as a hashtag."

    api = get_twitter_api()

    with open(f"{search_type}_tweets.csv", "w", encoding="utf8") as outfile:
        fieldnames = "id", "user_id", "screen_name", "text", "created_at"
        writer = DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for q in HASHTAGS[search_type]:
            for tweet in tweepy.Cursor(
                api.search,
                tweet_mode="extended",
                lang="en",
                q=q,
                since=since,
                until=until,
            ).items(count):
                write_tweet_to_csv(writer, tweet)


@cli.command()
@click.argument("input")
@click.argument("output")
@click.option(
    "--user_id_column",
    default="user_id",
    help="INPUT CSV file's user_id column to use",
)
@click.option(
    "--sample_size", default=100, help="How many followers to randomly sample"
)
def followers(input, output, user_id_column, sample_size):
    """INPUT: CSV file containing user_ids
       OUTPUT: CSV file with from_user_ids and to_user_ids"""

    api = get_twitter_api()

    with open(output, "w") as outfile:
        fieldnames = "from_user_id", "to_user_id"
        writer = DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for value in get_column_from_csv(input, user_id_column):

            try:
                from_user_ids = api.followers_ids(screen_name=value)
            except tweepy.TweepError:
                continue

            if len(from_user_ids) > sample_size:
                from_user_ids = sample(from_user_ids, sample_size)

            for from_user_id in from_user_ids:
                writer.writerow(
                    {"from_user_id": from_user_id, "to_user_id": value}
                )


@cli.command()
@click.argument("input")
@click.argument("output")
@click.option("--count", "-c", default=100, help="Number of tweets to pull")
@click.option("--since", "-s", default="2018-10-01")
@click.option("--until", "-u", default="2018-11-20")
@click.option(
    "--user_id_column",
    default="user_id",
    help="INPUT CSV file's user_id column to use",
)
def timeline(input, output, count, since, until, user_id_column):
    """INPUT: CSV file containing user_ids
       OUTPUT: CSV file with users' tweet timelines"""

    api = get_twitter_api()

    with open(output, "w", encoding="utf8") as outfile:
        fieldnames = "id", "user_id", "screen_name", "text", "created_at"
        writer = DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for user_id in get_column_from_csv(input, user_id_column):
            try:
                for tweet in tweepy.Cursor(
                    api.user_timeline,
                    user_id=user_id,
                    tweet_mode="extended",
                    lang="en",
                    since=since,
                    until=until,
                ).items(count):
                    write_tweet_to_csv(writer, tweet)
            except tweepy.TweepError:
                continue


if __name__ == "__main__":
    cli()
