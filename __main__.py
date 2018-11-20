from configparser import ConfigParser
import os

import twitter


def read_config(path="config"):
    if os.path.exists(path):
        config = ConfigParser()
        config.read(path)
        return config
    raise RuntimeError(f"Missing {path} config file")


def main():

    config = read_config()

    api = twitter.Api(
        consumer_key=config.get("twitter", "consumer_key"),
        consumer_secret=config.get("twitter", "consumer_secret"),
        access_token_key=config.get("twitter", "access_token"),
        access_token_secret=config.get("twitter", "access_token_secret"),
    )


if __name__ == "__main__":
    main()
