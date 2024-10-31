from enum import StrEnum
import polars as pl
#import tensorflow as tf

class EvaluationEnum(StrEnum):
    NOT_EVALUATED = "NOT_EVALUATED"



class EvaluateUrl:
    def __init__(self, url: str, body: str):
        self.url: str = url
        self.body: str = body
        self.evaluated = False
        self.evaluation: EvaluationEnum = EvaluationEnum.NOT_EVALUATED

    def __repr__(self):
        return f"URL({self.url})"
    def __str__(self):
        return self.url

    @staticmethod
    def to_polars(urls):
        return pl.DataFrame({'urls': [url.url for url in urls]})

    @staticmethod
    def to_tensorflow(urls):
        url_list = [url.url for url in urls]
        dataset = tf.data.Dataset.from_tensor_slices(url_list)
        return dataset
