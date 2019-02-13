import logging
import re
import time
from abc import abstractmethod
from typing import Tuple, Optional

from slackclient import SlackClient

from slack_bot.exceptions import SlackClientConnectionFailed

logger = logging.getLogger(__name__)


class BaseBot:
    RTM_READ_DELAY = 0.5
    MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

    def __init__(self, token: str):
        self.bot_id = None
        self.slack_client = SlackClient(token)
        self._check_connection()
        self.bot_id = self._get_user_id()

    def activate(self):
        logger.info("Slack bot running!")
        while True:
            slack_events = self._get_slack_events()
            command, channel = self._parse_bot_commands(slack_events)
            if command:
                self.handle_command(command, channel)
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

    def _is_message_to_bot(self, user_id: str) -> bool:
        return user_id == self.bot_id

    def _check_connection(self):
        if self.slack_client.rtm_connect(with_team_state=False):
            logger.info("Slack bot connected!")
        else:
            logger.error("Slack bot connection failed!")
            raise SlackClientConnectionFailed

    @abstractmethod
    def handle_command(self, command: str, channel: str) -> None:
        """Inheritors should implement this"""
        pass
