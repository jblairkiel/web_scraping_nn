import plotly.express as px
import pandas as pd
import polars as pl

class Hist():
    
    def __init__(self, title: str, df: pd.DataFrame|pl.DataFrame, x_attr: str, output_file: str):
        self.title = title
        self.df = df
        self.x_attr = x_attr
        self.output_file = output_file

    def plot(self):

        chart = px.histogram(
            x=self.df[self.x_attr],
            title=self.title
        )
        chart.write_html(self.output_file)