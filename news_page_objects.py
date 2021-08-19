import requests
import lxml.html as html
from common import config

class NewsPage:

    def __init__(self, news_site_uid: str, url: str) -> None:
        self.__config = config()["news_sites"][news_site_uid]
        self._queries = self.__config["queries"]
        self._html = None

        self._visit(url)

    def _select(self, query_string):
        return self._html.xpath(query_string)

    def _visit(self, url: str) -> None:
        response = requests.get(url)
        response.raise_for_status()

        page = response.content.decode("utf-8")
        self._html = html.fromstring(page)

class HomePage(NewsPage):

    def __init__(self, news_site_uid: str, url: str) -> None:
        super().__init__(news_site_uid, url)

    @property
    def article_links(self):
        return { link for link in self._select(self._queries["homepage_article_links"]) if link }

class ArticlePage(NewsPage):

    def __init__(self, news_site_uid: str, url: str) -> None:
        super().__init__(news_site_uid, url)

    @property
    def body(self):
        try:
            result = self._select(self._queries["article_body"])
            return result[0].replace('"', '') if len(result) else ""
        except IndexError:
            return ""

    @property
    def title(self):
        try:
            result = self._select(self._queries["article_title"])
            return result[0].replace('"', '') if len(result) else ""
        except IndexError:
            return ""

