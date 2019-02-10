import logging

from config import SLACK_BOT_TOKEN
from slack_handler import SlackHandler

logging.basicConfig(level=logging.INFO)


def main():
    slack_handler = SlackHandler(SLACK_BOT_TOKEN)
    slack_handler.activate_bot()


if __name__ == "__main__":
    main()
