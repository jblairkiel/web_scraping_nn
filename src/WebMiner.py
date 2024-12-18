from typing import List
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from collections import Counter
import time
import random
import csv
import re
from pathlib import Path
import pandas as pd
from model.EvaluateUrl import EvaluateUrl, EvalauatedUrlContainer
from plots.hist import Hist
from src.plots.bar import Bar

class WebMiner:
    def __init__(self, start_url, max_urls=100):
        self.urls_collected = []
        self.max_urls = max_urls
        self.evaluted_url_container: EvalauatedUrlContainer = EvalauatedUrlContainer(start_url, max_urls)
        self.urls_visited = []
        self.existing_links_path = Path("visited.parquet")
        if self.existing_links_path.exists():
            self.evaluted_url_container.load(self.existing_links_path)
            

    def fetch_page_data(self, url):
        ret_val = None
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                tags = ['p', 'span', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
                text_elements = []

                for tag in tags:
                    text_elements.extend([element.get_text() for element in soup.find_all(tag)])

                links: List[str] = set([a['href'] for a in soup.find_all('a', href=True) if 'http' in a['href'] and a['href'] not in self.urls_visited and not a['href'].endswith(('.jpg', '.png', '.gif')) and not "video" in a['href']])

                text_content = ' '.join(text_elements)
                ret_val = EvaluateUrl(url, body=text_content, links=links)
            #return {'url': url, 'text_content': text_content, 'links': links}

        except requests.exceptions.Timeout:
            print(f"Request to {url} timed out.")
        return ret_val


    def worker(self, url):
        data = None
        if is_valid_regex(url):
            data = self.fetch_page_data(url)
            if data is not None:
                data.remove_visited(self.urls_visited)
        return data
    
    def mine(self):

        iter = 0
        with tqdm(total=self.max_urls) as pbar:
            while self.evaluted_url_container.still_urls_to_visit():
                next_url = self.evaluted_url_container.pop_next_url()
                new_url_result_obj: EvaluateUrl = self.worker(next_url) #TODO Error here
                if iter == 10:
                    iter = 0
                    continue; 
                time.sleep(random.uniform(.5, 1.5))
                if new_url_result_obj is not None:
                    self.evaluted_url_container.add_new(new_url_result_obj)
                    pbar.update(1)
                    self.evaluted_url_container.urls_to_visit_iter = self.evaluted_url_container.urls_to_visit_iter + 1
                else:
                    self.evaluted_url_container.remove_url(next_url)
                iter = iter + 1
                



        self.evaluted_url_container.to_parquet("visited.parquet")
        df = self.evaluted_url_container.to_pandas()

        df['short_url'] = df['url'].apply(lambda x: x.split('.com')[0])
        a = Hist("Summary Urls", df, "short_url", "./urls_hist.html")
        a.plot()

        
        # a = Hist("Summary Urls", df, "links", "./links.html")
        # a.plot()



        # Flatten the dictionaries and extract all values 
        all_values = [value for dict_row in df['most_comon_words'] for value in dict_row.values()] 
        # Count the occurrences of each string 
        word_counts = Counter(all_values) 
        # Get the top 100 most common strings 
        top_100 = word_counts.most_common(100)
        counted_words_df = pd.DataFrame(top_100, columns=['word', 'occurrences'])
        
        a = Bar("Most Common Words", counted_words_df, "word", "occurrences", "./most_common_words.html")
        a.plot()

        return self.evaluted_url_container

def is_valid_regex(http: str):
    url_regex = re.compile(
        r'^(https?://)'  # http or https
        r'([a-zA-Z0-9.-]+)'  # domain name
        r'(\.[a-zA-Z]{2,6})'  # top-level domain
        r'([/a-zA-Z0-9.-]*)*'  # path
        r'/?$'  # end of string
    )
    return bool(url_regex.match(http))
