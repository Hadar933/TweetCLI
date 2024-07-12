# Tweet CLI Tool
This is a simple CLI tool to post tweets with optional media attachments using the Twitter API. The tool supports splitting long tweets into multiple parts if necessary and logs the process for better visibility.
![](https://github.com/Hadar933/TweetCLI/blob/main/media/tweet-cli-flow.gif)

## New
1. Use the `-a` or `--automate` to quickly tweet without having to answer user inputs. Usage: 
   ```
   tweet "heres my automated tweet" -a
   ```
2. pipe `tweet` with `at` to schedule tweets for later (only works with tweet automation `-a`):
   ```
   tweet "Hi from 1 minute to the future" -a | at now + 1 minute
   ```
   Note that this requires installing `at`: use `sudo apt-get install at`


## Features

- 📷 Post a tweet with text and optional media (with automated use-last-screenshot option).
- ✂️ Automatically split long tweets into multiple parts.
- #️⃣ prompt the user to add hashtags, if forgotten.
- 📝 Log detailed information about the tweet and its comments.
- 🌐 Optionally open the posted tweet in a web browser.

## Installation
(Tested on Ubuntu 24.04)
1. clone the repo
```sh
   git clone https://github.com/Hadar933/TweetCLI.git
   cd tweetcli

```
2. install requirements `pip install -r requirements`
3. enter [X Developer Dashboard ](https://developer.twitter.com/en/portal/petition/essential/basic-info), ramp up an App, and create a Consumer Keys, Bearer Token, and Access Token and Secret (under PRojects & Apps -> your app project -> keys and tokens)
4. Create a `.env` in the top scope and add the relevant keys:
```
BEARER_TOKEN=...
ACCESS_TOKEN=...
ACCESS_TOKEN_SECRET=...
CONSUMER_KEY=...
CONSUMER_SECRET=...
```
5. Set an alias: Add the following line to your .bashrc or .bash_profile (using `nano ~/.bashrc` for example to open it):
   ```
   alias tweet="source /path/to/.venv/bin/activate; python /path/to/tweetcli/tweet.py"
   ```
   then reload with `source ~/.bashrc`

## Usage
To use the CLI tool, run the following command:
tweet "Your tweet text here" -m path/to/media1 ... path/to/mediaN -u username

### Options
(run `tweet -h` to see)
positional arguments:
  tweet                 Text content of the tweet

options:
  * -h, --help            show this help message and exit
  * -m path [path ...], --media path [path ...]
                        Path(s) to media file(s) to attach to the tweet
  * -v, --verbose         Print verbose logging information
  * -u USERNAME, --username USERNAME
                        Username of the account to post the tweet to.
  * -s SCREENSHOT_PATH, --screenshot_path SCREENSHOT_PATH
                        Path to the screenshots directory, from which the latest image will be
                        fetched when posting (if desired).
  * -a, --automatic       Automatically post the tweet without asking for confirmation/other
                        inputs.


### Example:
```
hadar@laptop:~$ tweet "TweetCLI helps me post 3 times a day without issues. 🎉"
No hashtags found in tweet. Add? [y/n]: y
Enter hashtags separated by commas: python, cli
2024-07-12 19:10:07 | INFO | Tweet Length: 76
2024-07-12 19:10:07 | INFO | Splitting to 1 parts[1 Tweet + 0 Comment(s)].
Tweet:
------
TweetCLI helps me post 3 times a day without issues. 🎉 #python #cli
==================================================

Fetch latest screenshot? [y/n]: y
2024-07-12 19:10:16 | INFO | Latest screenshot file: /example/img.jpg
Post tweet? [y/n]: y
Open tweet in browser? [y/n]: y
```

## Licence

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Hadar933/TweetCLI/tree/main?tab=MIT-1-ov-file) file for details.


