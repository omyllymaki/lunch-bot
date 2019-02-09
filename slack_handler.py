import logging
import re
import time
from typing import Tuple, Optional, List, Any

from slackclient import SlackClient

from crawlers.turku_lunch_crawler import TurkuLunchCrawler

logger = logging.getLogger(__name__)


class SlackHandler:
    RTM_READ_DELAY = 1
    GREETINGS_COMMANDS = ["moi", "moro", "terve"]
    ALL_RESTAURANTS_COMMANDS = ["lounaat", "lounaslistat"]
    SINGLE_RESTAURANT_COMMANDS = ["lounas"]
    MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

    def __init__(self, token: str):
        self.bot_id = None
        self.slack_client = SlackClient(token)

    def start_slack_polling(self):
        if self._is_slack_client_connected():
            logger.info("Slack bot connected and running!")
            self.bot_id = self._get_user_id()

            while True:
                slack_events = self._get_slack_event()
                command, channel = self._parse_bot_commands(slack_events)
                if command:
                    self._handle_command(command, channel)
                time.sleep(self.RTM_READ_DELAY)
        else:
            logger.warning("Connection failed. Exception traceback printed above.")

    def post_message(self, channel: str, message: str) -> None:
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message
        )

    def _get_slack_event(self):
        return self.slack_client.rtm_read()

    def _get_user_id(self) -> str:
        return self.slack_client.api_call("auth.test")["user_id"]

    def _parse_bot_commands(self, slack_events) -> Tuple[Optional[str], Optional[str]]:
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = self._parse_direct_mention(event["text"])
                if self._is_message_to_bot(user_id):
                    return message, event["channel"]
        return None, None

    def _parse_direct_mention(self, message_text: str) -> Tuple[Optional[str], Optional[str]]:
        matches = re.search(self.MENTION_REGEX, message_text)
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def _handle_command(self, command: str, channel: str) -> None:
        response_text = f"Mitä meinaat? Kokeile vaikkapa jotain näistä: {self.ALL_RESTAURANTS_COMMANDS}"
        if self._is_item_in_list(command, self.GREETINGS_COMMANDS):
            response_text = "Morjestaaa!"
        if self._is_item_in_list(command, self.ALL_RESTAURANTS_COMMANDS):
            crawler = TurkuLunchCrawler()
            data = crawler.crawl()
            response_text = self._format_message_to_slack(data)
        if self._is_item_in_list(command, self.SINGLE_RESTAURANT_COMMANDS):
            restaurant = ' '.join(command.split()[1:])
            crawler = TurkuLunchCrawler()
            data = crawler.crawl()
            data_for_restaurant = data.get(restaurant, ['Ravintolalle ei löydy tietoja'])
            response_text = self._format_message_to_slack({restaurant: data_for_restaurant})
        self.post_message(channel=channel, message=response_text)

    def _is_message_to_bot(self, user_id: str) -> bool:
        return user_id == self.bot_id

    def _is_slack_client_connected(self):
        return self.slack_client.rtm_connect(with_team_state=False)

    @staticmethod
    def _is_item_in_list(target_item: str, item_list: List[str]) -> bool:
        return any([target_item.startswith(item) for item in item_list])

    @staticmethod
    def _format_message_to_slack(data: Any) -> str:
        formatted_text = ""
        for header, options in data.items():
            formatted_text += '\n'
            formatted_text += f'*{header}*' + '\n'
            for option in options:
                formatted_text += f'•{option}' + '\n'
        return formatted_text
