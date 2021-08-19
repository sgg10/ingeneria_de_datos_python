import argparse
import logging
import os
import sys
from urllib.parse import urlparse
import numpy as np
import pandas as pd
import hashlib
import nltk
from nltk.corpus import stopwords

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Execute only once
# nltk.download("punkt")
# nltk.download("stopwords")

stop_words = set(stopwords.words("spanish"))

def get_diff(files, dataframes):
    diff_between_files = {}
    diff_items = set()
    for f in files:
        for f2 in files:
            try:
                if f == f2 or f"{f2} -- {f}" in diff_between_files.keys():
                    continue
                diff = set(dataframes[f].columns) ^ set(dataframes[f2].columns)
                if len(diff):
                    diff_between_files[f"{f} -- {f2}"] = diff
                    diff_items.update(diff)
            except KeyError as error:
                print(f"File not found --> {error}")
    return diff_between_files, diff_items

def read_dataframes(files):
    dataframes = {}
    not_working = []
    concatenated_dataframe = None
    for file in files:
        try:
            df = pd.read_csv(file)
            df["origin_path"] = file
            dataframes[file.split("/")[-1]] = df
        except Exception as e:
            logger.warning(e)
            not_working.append(file)

    if not len(get_diff(list(dataframes.keys()), dataframes)[1]):
        concatenated_dataframe = pd.concat([ dataframes[df] for df in dataframes.keys() ]).reset_index(drop=True)
    return concatenated_dataframe, not_working

def extract_newspaper_uid(df):
    logger.info("Extracting newspaper uid")
    df["newspaper_uid"] = df['url'].apply(lambda url: urlparse(url).netloc.replace("www.", "").split(".")[0])
    return df

def extract_host(df):
    logger.info("Extracting newspaper host")
    df["host"] = df['url'].apply(lambda url: urlparse(url).netloc)
    return df

def clean_dataframe(df):
    logger.info("Cleaning data")
    for column in df.columns:
        df[column] = df[column].apply(lambda value: value.replace("\t", "").replace("\r", "").replace("\n", ""))
        df[column] = df[column].apply(lambda value: value.replace('"', ""))
        df[column] = df[column].apply(lambda value: value.strip())
    df.drop_duplicates(subset=["title"], keep="first", inplace=True)
    return df

def tokenize_column(df, column_name):
    logger.info(f"Tokenize {column_name} column")
    return (df
        .dropna()
        .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
        .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
        .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
        .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
        .apply(lambda valid_word_list: len(valid_word_list))
    )

def enrichment_colums(df):
    df["n_tokens_title"] = tokenize_column(df, "title")
    df["n_tokens_body"] = tokenize_column(df, "body")
    return df

def generate_uids(df):
    logger.info("Generating UIDs")
    uids = (
            df
                .apply(lambda row: hashlib.md5(bytes(row["url"].encode())),axis=1)
                .apply(lambda hash_obj: hash_obj.hexdigest())
        )
    df["uid"] = uids
    return df.set_index("uid")

def save_dataframe(df, name):
    df.to_csv(name, sep="|", encoding="utf-8")

def main(files):
    print(files)
    logger.info("Starting process")

    concatenated_dataframe, not_working = read_dataframes(files)

    if len(not_working):
        logger.warning(f"Not working files: {not_working}")
        logger.info("Skip these files")

    if concatenated_dataframe is not None:
        concatenated_dataframe = clean_dataframe(concatenated_dataframe)
        concatenated_dataframe = extract_newspaper_uid(concatenated_dataframe)
        concatenated_dataframe = extract_host(concatenated_dataframe)
        concatenated_dataframe = generate_uids(concatenated_dataframe)

        logger.info("Data enrichment")
        concatenated_dataframe = enrichment_colums(concatenated_dataframe)

    return concatenated_dataframe

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--files",
        help="files with the dirty data",
        nargs="+",
        default=[],
        required=False
    )
    args = parser.parse_args()
    if not len(args.files):
        print("You need to add --list argument to continue. Use -h flag to more information.")
        sys.exit()
    df = main(args.files)
    save_dataframe(df, name=f"final_datasets/clean_newspapers_articles.csv")
    # print(df["title"][df["body"].str.contains("Vicente Fernández Jr. aseguró que los rumore")])
    #print(np.unique([len(title) for title in df["title"]], return_counts=True))