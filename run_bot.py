import logging

from slack_bot.lunch_bot import LunchBot
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv(".env")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", None)


def main():
    bot = LunchBot(SLACK_BOT_TOKEN)
    bot.activate()


if __name__ == "__main__":
    main()
