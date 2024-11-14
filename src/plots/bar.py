import plotly.express as px
import pandas as pd
import polars as pl

class Bar():
    
    def __init__(self, title: str, df: pd.DataFrame|pl.DataFrame, x_attr: str,y_attr: str, output_file: str):
        self.title = title
        self.df = df
        self.x_attr = x_attr
        self.y_attr = y_attr
        self.output_file = output_file

    def plot(self):

        chart = px.bar(
            x=self.df[self.x_attr],
            y=self.df[self.y_attr],
            title=self.title
        )
        chart.write_html(self.output_file)