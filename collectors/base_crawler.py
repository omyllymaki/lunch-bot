from abc import abstractmethod

from requests import get
from typing import List, Dict


class BaseCrawler:
    def __init__(self, url: str):
        self.url = url
        self._get_response()

    def _get_response(self):
        self.response = get(self.url)

    @abstractmethod
    def crawl(self) -> Dict[str, List[str]]:
        raise NotImplementedError