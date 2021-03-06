import argparse
from common import config
from requests.models import HTTPError
from urllib3.exceptions import MaxRetryError
import logging
import re
from datetime import datetime
import csv

import news_page_objects as news

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

IS_WELL_FOR_LINK = re.compile(r'^https?://.+/.+$')
IS_ROOT_PATH = re.compile(r'^/.+$')


def _news_scraper(news_site_uid):
    host = config()["news_sites"][news_site_uid]["url"]

    logger.info(f"Beginning scraper for {host}")

    homepage = news.HomePage(news_site_uid, host)

    articles = []
    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, host, link)

        if article:
            logger.info("Article fetched!!")
            articles.append(article)
            print(article.title)

    _save_articles(news_site_uid, articles)

def _save_articles(news_site_uid, articles):
    now = datetime.now().strftime('%Y_%m_%d')
    out_file_name = f"extract/dirty_data/{news_site_uid}_{now}_articles.csv"
    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))
    with open(out_file_name, "w") as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers)

        for article in articles:
            row = [ str(getattr(article, prop)) for prop in csv_headers ]
            writer.writerow(row)

def _build_link(host, link):
    if IS_WELL_FOR_LINK.match(link):
        return link
    elif IS_ROOT_PATH.match(link):
        return f"{host}{link}"
    return f"{host}/{link}"

def _fetch_article(news_site_uid, host, link):
    logger.info(f"Start fetching article at {link}")

    article = None

    try:
        article = news.ArticlePage(news_site_uid, _build_link(host, link))
    except (HTTPError, MaxRetryError) as e:
        logger.warning(f"Error while fetching the article", exc_info=False)

    if article and not article.body:
        logger.warning("Invalid article. There is no body")
        return None

    return article

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    new_site_choices = list(config()["news_sites"].keys())

    parser.add_argument(
        'news_site',
        help="The news site that you want to scrape.",
        type=str,
        choices=new_site_choices
    )

    args = parser.parse_args()
    _news_scraper(args.news_site)