#!/usr/bin/env python3

# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧
# ⫷                                       IMPORTS                                          ⫸
# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧

import tweepy
from dotenv import load_dotenv
import os
from loguru import logger
import webbrowser
import argparse
from pathlib import Path


# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧
# ⫷                                       CONSTANTS                                        ⫸
# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧

SEE_NEXT_TWEET = "[...]"
MAX_TWEET_LEN = 280
MAX_TWEET_LEN -= len(SEE_NEXT_TWEET)

# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧
# ⫷                                       lOADING ENV                                      ⫸
# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧

loaded = load_dotenv()
if not loaded:
    raise ValueError("No .env file found")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
assert CONSUMER_KEY, "CONSUMER_KEY not found in .env"
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
assert CONSUMER_SECRET, "CONSUMER_SECRET not found in .env"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
assert ACCESS_TOKEN, "ACCESS_TOKEN not found in .env"
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
assert ACCESS_TOKEN_SECRET, "ACCESS_TOKEN_SECRET not found in .env"
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
assert BEARER_TOKEN, "BEARER_TOKEN not found in .env"

# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧
# ⫷                                 Utility Functions                                       ⫸
# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧


def _split_tweet(
        tweet: str
) -> list[str]:
    """
    Split the tweet into multiple tweets with a maximum length of MAX_TWEET_LEN.
    """
    tweet_list = []
    while len(tweet) > MAX_TWEET_LEN:
        # Find the last point before MAX_TWEET_LEN
        truncated = tweet[:MAX_TWEET_LEN]
        last_point_idx = truncated.rfind(".")
        last_comma_idx = truncated.rfind(",")
        last_idx = max(last_point_idx, last_comma_idx)
        if last_idx == -1:  # If , split at MAX_TWEET_LEN
            last_idx = MAX_TWEET_LEN
        tweet_list.append(tweet[:last_idx]+SEE_NEXT_TWEET)
        tweet = tweet[last_idx + 1:]
    tweet_list.append(tweet)
    return tweet_list


def _log_tweet(
        orig_tweet: str,
        tweet_list: list[str]
) -> None:
    """
    logs an informative representation of the tweet and its comments.
    :param orig_tweet: The original tweet, before splitting.
    :param tweet_list: List of tweets to log. (return value of _split_tweet)
    """
    logger.info(f"Tweet Length: {len(orig_tweet)}")
    logger.info(
        f"Splitting to {len(tweet_list)} parts"
        f"[1 Tweet + {len(tweet_list) - 1} Comment(s)]."
    )
    tweet_repr = f"\nTweet:\n{'-'*6}\n{tweet_list[0]}\n{'='*50}\n"
    comment_repr = ''
    for i, comment in enumerate(tweet_list[1:]):
        comment_repr += f"⪧ Comment #{i+1}:\n{'-'*10}\n{comment}\n{'-'*10}\n"
    logger.info(tweet_repr + comment_repr)


def _possibly_open_tweet(user_name: str, tweet_id: str) -> None:
    choice = input(f"Open tweet in browser? [y/n]: ")
    if choice.lower() == 'y' or choice.lower() == 'yes':
        url = f"https://x.com/{user_name}/status/{tweet_id}"
        webbrowser.open(url)


def get_latest_screenshot(directory: str) -> str | None:
    try:
        files = list(Path(directory).glob('*.png'))
        if not files:
            logger.error("No screenshot files found in the directory.")
            return None
        latest_file = max(files, key=os.path.getmtime)
        logger.info(f"Latest screenshot file: {latest_file}")
        return latest_file
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

    # ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧
    # ⫷                                       MAIN LOGIC                                       ⫸
    # ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧


def post(
    tweet: str,
    username: str,
    media_paths: list[str],
    verbose: bool,
    screenshot_path: str
):
    """
    Post a tweet to the authenticated account.
    :param tweet: The tweet to post - string or path to a file containing the tweet.
    :param media_path: Path(s) to an optional media to post with the tweet.
    :param verbose: Print logging information.

    """
    if os.path.exists(tweet):
        with open(tweet, 'r') as f:
            tweet = f.read()
    if media_paths:
        for media_path in media_paths:
            if not os.path.exists(media_path):
                raise FileNotFoundError(f"Media file {media_path} not found.")
    client = tweepy.Client(
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        bearer_token=BEARER_TOKEN
    )
    api = tweepy.API(
        auth=tweepy.OAuth1UserHandler(
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET,
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET
        )
    )
    tweet_list = _split_tweet(tweet)
    if verbose:
        _log_tweet(tweet, tweet_list)

    main_tweet = tweet_list[0]
    media_ids = None
    if media_paths:
        media_ids = []
        for media_path in media_paths:
            media_id = api.media_upload(media_path).media_id
            media_ids.append(media_id)
    else:
        screenshot = input("Fetch latest screenshot? [y/n]: ")
        if screenshot.lower() == 'y' or screenshot.lower() == 'yes':
            screenshot_path = get_latest_screenshot(screenshot_path)
            if screenshot_path:
                media_id = api.media_upload(screenshot_path).media_id
                media_ids = [media_id]

    approve = input("Post tweet? [y/n]: ")
    if approve.lower() != 'y' and approve.lower() != 'yes':
        logger.info("Tweet not posted.")
        return

    if media_ids is not None:
        response = client.create_tweet(text=main_tweet, media_ids=media_ids)
    else:
        response = client.create_tweet(text=main_tweet)

    tweet_id = response.data['id']
    if len(tweet_list) > 1:
        for comment in tweet_list[1:]:
            client.create_tweet(text=comment, in_reply_to_tweet_id=tweet_id)

    _possibly_open_tweet(username, tweet_id)


def main():
    DEBUG = False
    if DEBUG:
        tweet = "This is a test tweet. "
        media_paths = []
        username = "SharvitHadar"
        verbose = True
    else:
        parser = argparse.ArgumentParser(
            description="Post a tweet with optional media.")
        parser.add_argument('tweet', type=str,
                            help="Text content of the tweet")
        parser.add_argument('-m', '--media', metavar='path', type=str,
                            nargs='+', help="Path(s) to media file(s) to attach to the tweet")
        parser.add_argument('-v', '--verbose', action='store_true', default=True,
                            help="Print verbose logging information")
        parser.add_argument('-u', '--username', type=str, default='SharvitHadar',
                            help="Username of the account to post the tweet to.")
        parser.add_argument('-s', '--screenshot_path', type=str, default="/home/hadar/Pictures/Screenshots"
                            help="Path to the latest screenshot to post with the tweet.")

        args = parser.parse_args()

        tweet = args.tweet.strip()
        media_paths = args.media if args.media else []
        verbose = args.verbose
        username = args.username
        screenshot_path = args.screenshot_path

    post(tweet, username=username, media_paths=media_paths,
         verbose=verbose, screenshot_path=screenshot_path)


if __name__ == "__main__":
    main()
