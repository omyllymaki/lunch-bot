import logging

from slack_bot.lunch_bot import LunchBot
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv(".env")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", None)


def main():
    slack_handler = LunchBot(SLACK_BOT_TOKEN)
    slack_handler.activate_bot()


if __name__ == "__main__":
    main()
