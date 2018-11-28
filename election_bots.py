from configparser import ConfigParser
from csv import DictReader, DictWriter
import click
from datetime import date
import os


import tweepy


DEMOCRATIC_HASHTAGS = [
    "#VoteAndrewGillum",
    "#CountEveryVote",
    "#VoteDesantis",
    "#DemForce",
    "#GillumForFlorida",
    "#GillumForGovernor",
    "#VoteBlue",
    "#NeverRonDeSantis",
    "#TrumpStooge",
    "#GillumForTheWin",
    "#BlueWave",
    "#BlueTsunami2018",
    "#BlueTsunami",
    "#BlueWave2018",
    "#FlipFloridaBlue",
    "#TeamGillum",
    "#GunsenseCandidate",
    "#VoteBlueToSaveAmerica",
    "#FloridaBlue",
    "#BillNelson4Senate",
    "#Gillum4Governor",
    "#GillumSurge",
    "#Gillum4Florida",
    "#VoteDem",
    "#fucktrump",
    "#VoteGillum",
    "#NelsonforSenate",
    "#Nelson4Senate",
    "#NelsonSenate",
    "#antitrump",
    "#dumptrump",
    "#fuckgop",
    "#rickscottisacrook",
    "#GOPTaxScam",
    "#NoScott",
    "#VoteBlue2018",
    "#ResistTrump",
    "#BillNelsonForSenate",
    "#BillNelsonSenate",
]

REPUBLICAN_HASHTAGS = [
    "#DrainTheSwamp",
    "#LockHerUp",
    "#MAGA",
    "#MAGATrain",
    "#FakeNewsMedia",
    "#FloridaGOP",
    "#VoteGOP",
    "#MAGARally",
    "#VoteRonDeSantis",
    "#RonDeSantisFL",
    "#DeSantisForFlorida",
    "#DeSantisForGovernor",
    "#VoteRed",
    "#JobsNotMobs",
    "#SocialistGillum",
    "#RedNationRising",
    "#RedWave",
    "#VoteDemsOut",
    "#VoteRed2018",
    "#VoteRedToSaveAmerica",
    "#VoteRepublican",
    "#TrumpTrain",
    "#DeSantisForGov",
    "#FloridaRed",
    "#SupportPOTUSAgenda",
    "#TeamDeSantis",
    "#BillNelsonOut",
    "#RepRonDeSantis",
    "#libtards",
    "#VoteRedToSaveAmerica",
    "#VoteDemsOut",
    "#GillumFBI ",
    "#GillumPrison ",
    "#GillumJail ",
    "#GillumFraud ",
    "#GillumLiar",
    "#VoteDesantis",
    "#libtard",
    "#VoteRickScott",
    "#VoteScott",
    "#Desantis4Gov",
    "#ScottForSenator",
    "#Scott4Senator",
    "#ScottForSenate",
    "#Scott4Senate",
]

FLORIDA_HASHTAGS = [
    "#gillum",
    "#andrewgillum",
    "#desantis",
    "#rondesantis",
    "#rickscott",
    "#scott",
    "#nelson",
    "#billnelson",
    "#floridaelection",
    "#floridarecount",
    "#floridapolitcs",
    "#2018midterms",
    "#flsenate",
    "#flgubernatorial",
    "#VoteAndrewGillum",
    "#VoteDesantis",
    "#FloridaGOP",
    "#VoteRonDesantis",
    "#GillumForFlorida",
    "#GillumForGovernor",
    "#NeverRonDeSantis",
    "#GillumForTheWin",
    "#RonDeSantisFL",
    "#DeSantisForFlorida",
    "#DeSantisForGovernor",
    "#FlipFloridaBlue",
    "#TeamGillum",
    "#DeSantisForGov",
    "#FloridaRed",
    "#FloridaBlue",
    "#BillNelson4Senate",
    "#Gillum4Governor",
    "#GillumSurge",
    "#Gillum4Florida",
    "#VoteGillum",
    "#NelsonforSenate",
    "#Nelson4Senate",
    "#NelsonSenate",
    "#TeamDeSantis",
    "#BillNelsonOut",
    "#RepRonDeSantis",
    "#rickscottisacrook",
    "#VoteDesantis",
    "#NoScott",
    "#BillNelsonForSenate",
    "#BillNelsonSenate",
    "#GillumFBI ",
    "#GillumPrison ",
    "#GillumJail ",
    "#GillumFraud ",
    "#GillumLiar",
    "#VoteRickScott",
    "#VoteScott",
    "#Desantis4Gov",
    "#ScottForSenator",
    "#Scott4Senator",
    "#ScottForSenate",
    "#Scott4Senate",
]


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


def get_user_ids_from_csv(file):
    with open(file) as csvfile:
        user_ids = [row["user_id"] for row in DictReader(csvfile)]
    return user_ids


def write_tweets_to_csv(writer, tweets):
    for tweet in tweets:
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
@click.option("--democratic/--republican", required=True)
@click.option("--since", "-s", default="2018-01-01")
@click.option("--until", "-u", default="2018-11-20")
@click.option("--count", "-c", default=2000, help="Number of tweets to pull")
def search(democratic, since, until, count):
    "OUTPUT: CSV file with tweets that match a query, such as a hashtag."

    hashtags = DEMOCRATIC_HASHTAGS if democratic else REPUBLICAN_HASHTAGS

    output = f"{'democratic' if democratic else 'republican'}_tweets.csv"

    api = get_twitter_api()

    with open(output, "w", encoding="utf8") as outfile:
        fieldnames = "id", "user_id", "screen_name", "text", "created_at"
        writer = DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for q in hashtags:
            tweets = tweepy.Cursor(
                api.search,
                tweet_mode="extended",
                lang="en",
                q=q,
                since=since,
                until=until,
            ).items(count)

            write_tweets_to_csv(writer, tweets)


@cli.command()
@click.argument("input")
@click.argument("output")
def followers(input, output):
    """INPUT: CSV file containing user_ids
       OUTPUT: CSV file with from and to user_ids"""

    api = get_twitter_api()

    with open(output, "w") as outfile:
        fieldnames = "from", "to"
        writer = DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for to in get_user_ids_from_csv(input):
            for _from in tweepy.Cursor(api.followers_ids, user_id=to):
                writer.writerow({"from": _from, "to": to})


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

            tweets = tweepy.Cursor(
                api.user_timeline,
                user_id=user_id,
                tweet_mode="extended",
                lang="en",
                since=since,
                until=until,
            ).items(100)

            write_tweets_to_csv(writer, tweets)


if __name__ == "__main__":
    cli()
