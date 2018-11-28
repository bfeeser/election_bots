# election_bots

Finding Twitter bots from the recent midterm elections.

For Operations Analytics (15.774) at MIT Sloan with [Tauhid Zaman](http://mitmgmtfaculty.mit.edu/zlisto/).

Please put your Twitter Developer Account credentials in `config`.

## Installation and Usage

```
$ # Install Python 3.7 and git
$ pip install pipenv
$ git clone git@github.com:bfeeser/election_bots.git
$ pipenv install
$ pipenv run python election_bot.py search --democratic
$ pipenv run python election_bot.py followers democratic_tweets.csv democratic_followers.csv
$ pipenv run python election_bot.py timeline
```
