from typing import Dict, List

from bs4 import BeautifulSoup
from selenium import webdriver


class TurkuLunchCrawler:
    URL = 'https://www.lounaat.info/turku'

    def crawl(self) -> Dict[str, List[str]]:
        html_text = self._get_html_text()
        self.parser = BeautifulSoup(html_text, 'html.parser')
        restaurant_containers = self._crawl_restaurant_containers()

        data = {}
        for container in restaurant_containers:
            restaurant_name = self._crawl_restaurant_name(container)
            lunch_options = self._crawl_lunch_options(container)
            data[restaurant_name] = lunch_options
        return data

    def _crawl_lunch_options(self, container):
        lunch_options = []
        lunch_containers = container.find_all('li', {'class': 'menu-item'})
        for container in lunch_containers:
            try:
                lunch_option = container.get_text()
            except AttributeError:
                lunch_option = None
            lunch_options.append(lunch_option)
        return lunch_options

    def _crawl_restaurant_name(self, container):
        try:
            restaurant_name = container.find('h3').get_text()
        except AttributeError:
            restaurant_name = None
        return restaurant_name

    def _get_html_text(self):
        driver = webdriver.Firefox()
        driver.get(self.URL)
        for k in range(5):
            driver.find_element_by_class_name("button.showmore").click()
        html_text = driver.page_source
        driver.close()
        return html_text

    def _crawl_restaurant_containers(self):
        return self.parser.find_all('div', {'class': 'isotope-item'})
