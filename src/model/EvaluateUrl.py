from collections import Counter
from enum import StrEnum
from typing import Any, Dict, List, Optional
import polars as pl
#import tensorflow as tf
import polars as pl
import pandas as pd

class EvaluationEnum(StrEnum):
    NOT_EVALUATED = "NOT_EVALUATED"

class EvalauatedUrlContainer:
    def __init__(self, start_url: str):
        self.data: Dict[int, EvaluateUrl] = {}
        self.iter = 0
        self.urls_to_visit = {}
        self.urls_visited = []
        self.urls_to_visit = {self.iter: start_url}
        self.iter = self.iter + 1
    
    def add_new(self, obj):
        self.data[self.iter] = obj
        new_urls = obj.links
        existing_urls = [key for key in self.urls_to_visit.keys()]
        for url in new_urls:
            if url not in existing_urls:
                self.urls_to_visit[url] = self.iter
        self.urls_visited.append(obj.url)
        self.iter = self.iter + 1

    def add(self, obj):
        self.data[self.iter] = obj
        self.iter = self.iter + 1

    def load(self, existing_links_parquet_path: str):
        df = pl.read_parquet(existing_links_parquet_path)
        for cur_row in df.iter_rows():    
            _url: str = cur_row[0]
            _links: List[str] = cur_row[1]
            _body: str = cur_row[2]
            _evaluated = cur_row[3]
            _evaluation: EvaluationEnum = cur_row[4]
            _most_common_words: Dict[str, str] = cur_row[5]
            self.add(EvaluateUrl(url=_url, links=_links, body=_body, evaluated=_evaluated, evaluation=_evaluation, most_common_words=_most_common_words))
    
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
        keys = [key for key in self.data.keys()]
        for cur_key in keys:
            try:
                print(f"\t{self.data[cur_key].url} - {self.data[cur_key].most_common_words}")
            except Exception as ex:
                print(f"Skipping: {cur_key}")



class EvaluateUrl:
    def __init__(self, url: str, body: str, links: List[str] = [], evaluated: bool = False, evaluation: EvaluationEnum= EvaluationEnum.NOT_EVALUATED, most_common_words: Optional[Dict[str, str]] = None):
        self.url: str = url
        self.links: List[str] = links
        self.body: str = body
        self.evaluated = evaluated
        self.evaluation: EvaluationEnum = evaluation
        if most_common_words is None:
            self.most_common_words = get_most_common_words(body)
        else:
            self.most_common_words = most_common_words
        

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
def get_most_common_words(text):
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
