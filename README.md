# Tweet CLI Tool
This is a simple CLI tool to post tweets with optional media attachments using the Twitter API. The tool supports splitting long tweets into multiple parts if necessary and logs the process for better visibility.

## Features

- 📷 Post a tweet with text and optional media.
- ✂️ Automatically split long tweets into multiple parts.
- 📝 Log detailed information about the tweet and its comments.
- 🌐 Optionally open the posted tweet in a web browser.

## Installation
1. clone the repo
```sh
   git clone https://github.com/hadar933/tweetcli.git
   cd tweetcli

```
2. install requirements `pip install -r requirements`
3. enter [X Developer Dashboard ](https://developer.twitter.com/en/portal/petition/essential/basic-info), ramp up an App and create a Consumer Keys, Bearer Token, and Access Token and Secret (under PRojects & Apps -> your app project -> keys and tokens)
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
tweet "Your tweet text here" -m path/to/media1 ... path/to/mediaN -u yourusername

### Options
(run `tweet -h` to see)
-  tweet: Text content of the tweet.
- -m path [path ...], --media path [path ...]: Path(s) to media file(s) to attach to the tweet.
- -v, --verbose: Print verbose logging information (default: True).
- -u USERNAME, --username USERNAME: Username of the account to post the tweet to.

### Example:
```
tweet "Check out this cool photo!" -m /path/to/photo.jpg -u SharvitHadar
```
This will post the tweet "Check out this cool photo!" with the attached photo to the specified user's account.

## Licence

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Hadar933/TweetCLI/tree/main?tab=MIT-1-ov-file) file for details.


