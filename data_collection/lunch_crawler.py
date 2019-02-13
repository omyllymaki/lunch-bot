import logging
from typing import Dict, List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException

logger = logging.getLogger(__name__)


class LunchCrawler:
    URL = 'https://www.lounaat.info/turku'
    NUMBER_OF_SHOW_MORE_CLICKS = 5

    def crawl(self):
        logger.info('Start data crawling')
        try:
            data = self._crawl_data()
        except Exception as e:
            logger.error(f'Data crawling failed. Error message: {e}')
            data = None
        logger.info('Data crawling finished')
        return data

    def _crawl_data(self) -> Dict[str, List[str]]:
        self._get_html_and_initialize_parser()
        restaurant_containers = self._crawl_restaurant_containers()
        data = {}
        for container in restaurant_containers:
            restaurant_name = self._crawl_restaurant_name(container)
            lunch_options = self._crawl_lunch_options(container)
            distance = self._crawl_distance(container)
            data[restaurant_name] = lunch_options
            logger.debug(f'{restaurant_name}, {distance}: {lunch_options}')
        return data

    def _get_html_and_initialize_parser(self):
        self.driver = webdriver.Firefox()
        html_text = self._get_html_text()
        self.driver.close()
        self.parser = BeautifulSoup(html_text, 'html.parser')

    def _crawl_lunch_options(self, container):
        lunch_options = []
        lunch_containers = container.find_all('li', {'class': 'menu-item'})
        for container in lunch_containers:
            try:
                lunch_option = container.get_text()
            except AttributeError:
                lunch_option = None
                logger.debug('Lunch not found')
            lunch_options.append(lunch_option)
        return lunch_options

    def _crawl_distance(self, container):
        try:
            distance = container.find('p', {'class': 'dist'}).get_text()
        except AttributeError:
            distance = None
            logger.debug('Distance not found')
        return distance

    def _crawl_restaurant_name(self, container):
        try:
            restaurant_name = container.find('h3').get_text()
        except AttributeError:
            restaurant_name = None
            logger.debug('Restaurant not found')
        return restaurant_name

    def _get_html_text(self):
        self.driver.get(self.URL)
        try:
            for k in range(self.NUMBER_OF_SHOW_MORE_CLICKS):
                self.driver.find_element_by_class_name("button.showmore").click()
            html_text = self.driver.page_source
        except ElementClickInterceptedException:
            logger.warning('Get HTML text failed. Refresh page and retry')
            self.driver.refresh()
            for k in range(self.NUMBER_OF_SHOW_MORE_CLICKS):
                self.driver.find_element_by_class_name("button.showmore").click()
            html_text = self.driver.page_source
        return html_text

    def _crawl_restaurant_containers(self):
        return self.parser.find_all('div', {'class': 'isotope-item'})
