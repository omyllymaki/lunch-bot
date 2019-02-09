from abc import abstractmethod

from bs4 import BeautifulSoup
from requests import get


class UnsuccessfulRequestError(Exception):
    pass


class BaseCrawler:
    SUCCESSFUL_RESPONSE_STATUS_CODE = 200
    VALUE_IF_NOT_FOUND = None

    def __init__(self, url: str) -> None:
        self.url = url
        self.response = None
        self.parser = None
        self._initialize_crawler()

    def _initialize_crawler(self) -> None:
        self._get_response()
        self._create_html_parser()

    def _create_html_parser(self) -> None:
        self.parser = BeautifulSoup(self.response.text, 'html.parser')

    def _get_response(self) -> None:
        self.response = get(self.url)
        self._check_response_status()

    def _check_response_status(self) -> None:
        if self.response.status_code != self.SUCCESSFUL_RESPONSE_STATUS_CODE:
            raise UnsuccessfulRequestError

    @abstractmethod
    def crawl(self, *args):
        raise NotImplementedError
