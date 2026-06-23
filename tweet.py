#!/usr/bin/env python3

# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧
# ⫷                                       IMPORTS                                          ⫸
# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧

import tweepy
from dotenv import load_dotenv
import os
import requests
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

load_dotenv()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} not found in environment or .env")
    return value


BACKEND = os.getenv("TWEETCLI_BACKEND", "twitter").strip().lower()
XQUIK_API_BASE_URL = os.getenv(
    "XQUIK_API_BASE_URL",
    "https://xquik.com/api/v1"
).rstrip("/")

if BACKEND == "twitter":
    CONSUMER_KEY = _required_env("CONSUMER_KEY")
    CONSUMER_SECRET = _required_env("CONSUMER_SECRET")
    ACCESS_TOKEN = _required_env("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = _required_env("ACCESS_TOKEN_SECRET")
    BEARER_TOKEN = _required_env("BEARER_TOKEN")
elif BACKEND == "xquik":
    XQUIK_API_KEY = _required_env("XQUIK_API_KEY")
    XQUIK_ACCOUNT = _required_env("XQUIK_ACCOUNT")
else:
    raise ValueError("TWEETCLI_BACKEND must be either 'twitter' or 'xquik'")

# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧
# ⫷                                 Utility Functions                                       ⫸
# ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧


def agree(user_input):
    return user_input.lower() == 'y' or user_input.lower() == 'yes'


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
        tweet_list: list[str],
) -> None:
    """
    logs an informative representation of the tweet and its comments.
    :param orig_tweet: The original tweet, before splitting.
    :param tweet_list: List of tweets to log. (return value of _split_tweet)
    :param automatic: Whether the tweet is being posted automatically.
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
    if agree(choice):
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


def add_hashtags(tweet: str) -> str:
    """ if the tweet is missing hashtags, prompt the user to add them. """
    if "#" not in tweet:
        add_hashtags = input("No hashtags found in tweet. Add? [y/n]: ")
        if agree(add_hashtags):
            input_hashtags = input("Enter hashtags separated by commas:")
            hashtags = [
                f"#{tag.strip()}" if '#' not in tag else tag.strip()
                for tag in input_hashtags.split(",")
            ]
            tweet += " " + " ".join(hashtags)
    return tweet

    # ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧
    # ⫷                                       MAIN LOGIC                                       ⫸
    # ⪦⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⩶⪧


def _post_xquik_tweet(tweet: str) -> str | None:
    response = requests.post(
        f"{XQUIK_API_BASE_URL}/x/tweets",
        headers={
            "Authorization": f"Bearer {XQUIK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "account": XQUIK_ACCOUNT,
            "text": tweet,
        },
        timeout=30,
    )

    try:
        response_data = response.json()
    except ValueError:
        response_data = {}

    if response.status_code == 202:
        write_action_id = response_data.get("writeActionId")
        logger.info(f"Xquik accepted the tweet. Write action: {write_action_id}")
        return None

    response.raise_for_status()

    tweet_id = (
        response_data.get("tweetId")
        or response_data.get("id")
        or response_data.get("data", {}).get("id")
    )
    if not tweet_id:
        raise ValueError("Xquik response did not include a tweet ID.")

    logger.info(f"Xquik posted tweet ID: {tweet_id}")
    return str(tweet_id)


def post(
    tweet: str,
    username: str,
    media_paths: list[str],
    verbose: bool,
    screenshot_path: str,
    automatic: bool
):
    """
    Post a tweet to the authenticated account.
    :param tweet: The tweet to post - string or path to a file containing the tweet.
    :param media_path: Path(s) to an optional media to post with the tweet.
    :param verbose: Print logging information.
    :param screenshot_path: Path to the screenshots directory.
    :param automatic: Automatically post the tweet without asking for confirmation/other inputs.
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
    if not automatic:
        tweet = add_hashtags(tweet)
    tweet_list = _split_tweet(tweet)
    if verbose:
        _log_tweet(tweet, tweet_list)

    if BACKEND == "xquik":
        if media_paths:
            raise ValueError(
                "Xquik backend in TweetCLI supports text tweets only. "
                "Use the default Twitter backend for local media uploads."
            )
        if len(tweet_list) > 1:
            raise ValueError(
                "Xquik backend in TweetCLI posts one text tweet at a time. "
                "Shorten the tweet or use the default Twitter backend for threads."
            )

        tweet_it = 'y' if automatic else input("Post tweet? [y/n]: ")
        if not agree(tweet_it):
            logger.info("Tweet not posted.")
            return

        tweet_id = _post_xquik_tweet(tweet_list[0])
        if tweet_id and not automatic:
            _possibly_open_tweet(XQUIK_ACCOUNT.lstrip("@"), tweet_id)
        return

    main_tweet = tweet_list[0]
    media_ids = None
    if media_paths:
        media_ids = []
        for media_path in media_paths:
            media_id = api.media_upload(media_path).media_id
            media_ids.append(media_id)
    else:
        screenshot = 'n' if automatic else input(
            "Fetch latest screenshot? [y/n]: ")
        if agree(screenshot):
            screenshot_path = get_latest_screenshot(screenshot_path)
            if screenshot_path:
                media_id = api.media_upload(screenshot_path).media_id
                media_ids = [media_id]

    tweet_it = 'y' if automatic else input("Post tweet? [y/n]: ")
    if not agree(tweet_it):
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
    if not automatic:
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
        parser.add_argument('-s', '--screenshot_path', type=str, default="/home/hadar/Pictures/Screenshots",
                            help="Path to the screenshots directory, from which the latest image will be fetched when posting (if desired).")
        parser.add_argument('-a', '--automatic', action='store_true',
                            help="Automatically post the tweet without asking for confirmation/other inputs.")
        args = parser.parse_args()

        tweet = args.tweet.strip()
        media_paths = args.media if args.media else []
        verbose = args.verbose
        username = args.username
        screenshot_path = args.screenshot_path
        automatic = args.automatic

    post(tweet, username=username, media_paths=media_paths,
         verbose=verbose, screenshot_path=screenshot_path, automatic=automatic)


if __name__ == "__main__":
    main()
