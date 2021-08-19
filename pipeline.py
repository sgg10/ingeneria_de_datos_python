import logging
import subprocess
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

news_sites_uids = ["eluniversal", "elpais"]

def extract():
    logger.info("Starting extract process")
    for news_site_uid in news_sites_uids:
        subprocess.run(["python", "extract/main.py", news_site_uid], cwd=".")
        # subprocess.run(["find", ".", "-name", f"{news_site_uid}*",
        #     "-exec", "mv", "{}", f"./dirty_data/{news_site_uid}.csv", ";"], cwd="./extract")

def transform():
    logger.info("Starting transform process")
    list_of_dirty_files = [
        f"extract/dirty_data/{file}"
        for file in os.listdir("extract/dirty_data")
        if os.path.isfile(os.path.join("extract/dirty_data", file))
    ]
    subprocess.run(["python", "transform/main.py", "--files"] + list_of_dirty_files , cwd=".")

def load():
    logger.info("Starting load process")
    subprocess.run(["python", "load/main.py", "transform/final_datasets/clean_newspapers_articles.csv"], cwd=".")

def main():
    extract()
    transform()
    load()

if __name__ == "__main__":
    main()