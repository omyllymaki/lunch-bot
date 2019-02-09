from config import SLACK_BOT_TOKEN
from slack_handler import SlackHandler
import logging

logging.basicConfig(level=logging.INFO)


def main():
    slack_handler = SlackHandler(SLACK_BOT_TOKEN)
    slack_handler.start_slack_polling()


if __name__ == "__main__":
    main()
