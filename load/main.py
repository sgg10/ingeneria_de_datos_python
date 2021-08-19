import argparse
import logging
import pandas as pd
from article import Article
from base import Base, engine, Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(filename):
    Base.metadata.create_all(engine)
    session = Session()
    articles = pd.read_csv(filename, sep="|")

    for idx, row in articles.iterrows():
        logger.info(f"Loading article uid {row['uid']} into DB")
        article = Article(
            uid = row["uid"],
            title = row["title"],
            body = row["body"],
            newspaper_uid = row["newspaper_uid"],
            n_tokens_title = row["n_tokens_title"],
            n_tokens_body = row["n_tokens_body"],
            host = row["host"],
            url = row["url"],
            origin = row["origin_path"]
        )
        session.add(article)

    session.commit()
    session.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        help="The file you want to load into the db",
        type=str
    )
    args = parser.parse_args()
    main(args.filename)