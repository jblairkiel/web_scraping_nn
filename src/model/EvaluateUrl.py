from collections import Counter
from enum import StrEnum
from typing import Any, Dict, List
import polars as pl
#import tensorflow as tf
import polars as pl
import pandas as pd

class EvaluationEnum(StrEnum):
    NOT_EVALUATED = "NOT_EVALUATED"

class EvalauatedUrlContainer:
    def __init__(self):
        self.data: Dict[int, EvaluateUrl] = {}
        self.iter = 0
    
    def add(self, obj):
        self.data[self.iter] = obj
        self.iter = self.iter + 1

    def load(self, existing_links_parquet_path: str):
        a = pl.read_parquet(existing_links_parquet_path)
        for link in a.iter_rows():
            self.add(link)
    
    def to_parquet(self, file_path):
        # Convert list of objects to DataFrame
        values = []
        try:
            for key in self.data.keys():
                values.append(self.data[key].to_dict() )
            polars_df = pl.from_dicts(values)
            # Save Polars DataFrame to Parquet file
            polars_df.write_parquet(file_path)
        except Exception as ex: 
            print("error here")
        
        

    def __str__(self):
        print("Data: ")
        for a in self.data:
            print(f"\t{a.url} - {a.most_common_words}")



class EvaluateUrl:
    def __init__(self, url: str, body: str, links: List[str] = []):
        self.url: str = url
        self.links: List[str] = links
        self.body: str = body
        self.evaluated = False
        self.evaluation: EvaluationEnum = EvaluationEnum.NOT_EVALUATED
        self.most_common_words: Dict[str, str] = most_common_words(body)

    def __repr__(self):
        return f"URL({self.url})"
    def __str__(self):
        return self.url
    
    def remove_visited(self, visited: List[str]):
        self.links = [link for link in self.links if link not in visited]

    def to_dict(self):
        return {
            "url": self.url,
            "links": self.links,
            "body": self.body,
            "evaluated": self.evaluated,
            "evaluation": self.evaluation,
            "most_comon_words": self.most_common_words

        }

@staticmethod
def most_common_words(text):
    word_count = Counter(text.split())
    stopwords = set(['&', 'the', 'and', 'a', 'to', 'of', 'in', 'that', 'is', 'for', 'on', 'with', 'as', 'it', 'are', 'was', 'at', 'be', 'by', 'this', 'an'])
    filtered_words = {word: count for word, count in word_count.items() if word.lower() not in stopwords}
    most_common = Counter(filtered_words).most_common(10)
    most_common_dict = {}
    i = 1
    for el, _ in most_common:
        most_common_dict[str(i)] = el
        i = i + 1
    return most_common_dict

    # @staticmethod
    # def to_tensorflow(urls):
    #     url_list = [url.url for url in urls]
    #     dataset = tf.data.Dataset.from_tensor_slices(url_list)
    #     return dataset
