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

from model.EvaluateUrl import EvaluateUrl, EvalauatedUrlContainer

class WebMiner:
    def __init__(self, start_url, max_urls=100):
        self.start_url = start_url
        self.urls_to_visit = [self.start_url]
        self.urls_collected = []
        self.urls_visited = []
        self.max_urls = max_urls
        self.evaluted_url_container: EvalauatedUrlContainer = EvalauatedUrlContainer()
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
            while self.urls_to_visit and len(self.urls_visited) < self.max_urls:
                new_url_result_obj: EvaluateUrl = self.worker(self.urls_to_visit[iter])
                time.sleep(random.uniform(.3, .9))
                if new_url_result_obj is not None:
                    new_urls = new_url_result_obj.links
                    self.evaluted_url_container.add(new_url_result_obj)
                    self.urls_visited.append(new_url_result_obj.url)
                    self.urls_to_visit.extend(new_urls)
                    pbar.update(1)
                    iter = iter = 1
                



        self.evaluted_url_container.to_parquet("visited.parquet")

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
