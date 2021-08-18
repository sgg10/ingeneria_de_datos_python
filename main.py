import argparse
from common import config
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def _news_scraper(news_site_uid):
    host = config()["news_sites"][news_site_uid]["url"]

    logging.info(f"Beginning scraper for {host}")

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