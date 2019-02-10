import logging
import random
import re
import time
from typing import Tuple, Optional, List, Any, Dict

from slackclient import SlackClient

from exceptions import SlackClientConnectionFailed
from turku_lunch_crawler import TurkuLunchCrawler

logger = logging.getLogger(__name__)


class SlackHandler:
    RTM_READ_DELAY = 1
    MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
    COMMANDS = {
        'instructions': ["ohje", "ohjeet"],
        'greeting': ["moi", "moro", "terve"],
        'all_lunch_options': ["lounaat", "lounaslistat"],
        'single_lunch_option': ["lounas"],
    }

    def __init__(self, token: str):
        self.bot_id = None
        self.slack_client = SlackClient(token)
        self.crawler = TurkuLunchCrawler()
        self._check_connection()

    def activate_bot(self):
        logger.info("Slack bot running!")
        self.bot_id = self._get_user_id()

        while True:
            slack_events = self._get_slack_events()
            command, channel = self._parse_bot_commands(slack_events)
            if command:
                self._handle_command(command, channel)
            time.sleep(self.RTM_READ_DELAY)

    def post_message(self, channel: str, message: str) -> None:
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message
        )

    def _get_slack_events(self):
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
        if matches:
            return matches.group(1), matches.group(2).strip()
        return None, None

    def _handle_command(self, command: str, channel: str) -> None:
        response_text = f"Mitä meinaat? Kokeile jotain näistä: {self.COMMANDS}"
        first_word = command.split()[0].lower()
        if first_word in self.COMMANDS['instructions']:
            response_text = self._handle_instructions()
        if first_word in self.COMMANDS['greeting']:
            response_text = self._handle_greeting()
        if first_word in self.COMMANDS['all_lunch_options']:
            response_text = self._handle_all_lunch_options()
        if first_word in self.COMMANDS['single_lunch_option']:
            response_text = self._handle_single_lunch_option(command)
        self.post_message(channel=channel, message=response_text)

    def _handle_instructions(self):
        response_text = f'Hei! Olen avulias lounasbotti, joka kertoo, mistä saa Turun parhaat sapuskat. Vastaan kutsuihin, jotka ovat muotoa @MinunNimeni kutsu. Tällä hetkellä tuettuja kutsuja ovat: {self.COMMANDS}.'
        return response_text

    def _handle_greeting(self):
        options = ['Morjestaa', 'Moro', 'Hei']
        return random.choice(options)

    def _handle_single_lunch_option(self, command: str) -> str:
        restaurant = ' '.join(command.split()[1:])
        data = self._get_lunch_data()
        data_for_restaurant = data.get(restaurant, ['Ravintolalle ei löydy tietoja'])
        response_text = self._format_message_to_slack({restaurant: data_for_restaurant})
        return response_text

    def _handle_all_lunch_options(self) -> str:
        data = self._get_lunch_data()
        response_text = self._format_message_to_slack(data)
        return response_text

    def _is_message_to_bot(self, user_id: str) -> bool:
        return user_id == self.bot_id

    def _check_connection(self):
        if self.slack_client.rtm_connect(with_team_state=False):
            logger.info("Slack bot connected!")
        else:
            logger.error("Slack bot connection failed!")
            raise SlackClientConnectionFailed

    def _get_lunch_data(self):
        try:
            data = self.crawler.crawl()
        except Exception as e:
            logger.error(f'Data crawling failed. Error message: {e}')
            data = {'Virhe': ['Tietojen hakemisessa tapahtui virhe']}
        return data

    @staticmethod
    def _format_message_to_slack(data: Any) -> str:
        formatted_text = ""
        for header, options in data.items():
            formatted_text += '\n'
            formatted_text += f'*{header}*' + '\n'
            for option in options:
                formatted_text += f'•{option}' + '\n'
        return formatted_text
