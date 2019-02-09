from typing import Dict, List

from collectors.base_crawler import BaseCrawler


class RootsCrawler(BaseCrawler):

    def __init__(self):
        url = 'https://www.lounaat.info/lounas/roots-kitchen/turku'
        super().__init__(url)

    def crawl(self) -> Dict[str, List[str]]:
        test_response = {
            'keitto': ['tomaattikeitto', 'kurpitakeitto'],
            'lämmin': ['punajuuripihvi']
        }
        return test_response
