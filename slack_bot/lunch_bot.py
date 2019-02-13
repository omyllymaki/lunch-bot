import logging
import random

from data_collection.lunch_crawler import LunchCrawler
from slack_bot.base_bot import BaseBot

logger = logging.getLogger(__name__)


class LunchBot(BaseBot):

    def __init__(self, token: str):
        super().__init__(token)
        self.crawler = LunchCrawler()
        self.intentions = {
            'instructions': {
                'input': ["ohje", "ohjeet"],
                'response': self._response_instructions,
            },
            'greeting': {
                'input': ["moi", "moro", "terve"],
                'response': self._response_greeting,
            },
            'all_lunch_options': {
                'input': ["lounaat", "lounaslistat"],
                'response': self._response_all_lunch_options,
            },
            'single_lunch_option': {
                'input': ["lounas"],
                'response': self._response_single_lunch_option,
            }
        }
        self.list_of_inputs = [v['input'] for v in self.intentions.values()]
        self.default_response = f"Mitä meinaat? Kokeile jotain näistä: {self.list_of_inputs}"

    def handle_command(self, command: str, channel: str) -> None:
        response_text = self.default_response
        self.command = command
        first_word = command.split()[0].lower()
        for intention, values in self.intentions.items():
            if first_word in values['input']:
                response_text = values['response']()
        self.post_message(channel=channel, message=response_text)

    def _response_instructions(self):
        response_text = f'Hei! Olen avulias lounasbotti, joka kertoo, mistä saa Turun parhaat sapuskat. ' \
                        f'Vastaan kutsuihin, jotka ovat muotoa @MinunNimeni kutsu. ' \
                        f'Tällä hetkellä tuettuja kutsuja ovat: {self.list_of_inputs}.'
        return response_text

    def _response_greeting(self):
        options = ['Morjestaa', 'Moro', 'Hei']
        return random.choice(options)

    def _response_single_lunch_option(self) -> str:
        restaurant = ' '.join(self.command.split()[1:])
        data = self._get_lunch_data()
        data_for_restaurant = data.get(restaurant, ['Ravintolalle ei löydy tietoja'])
        response_text = self._format_message_to_slack({restaurant: data_for_restaurant})
        return response_text

    def _response_all_lunch_options(self) -> str:
        data = self._get_lunch_data()
        response_text = self._format_message_to_slack(data)
        return response_text

    def _get_lunch_data(self):
        try:
            data = self.crawler.crawl()
        except Exception as e:
            logger.error(f'Data crawling failed. Error message: {e}')
            data = {'Virhe': ['Tietojen hakemisessa tapahtui virhe']}
        return data
