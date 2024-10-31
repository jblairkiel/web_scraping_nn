from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool, Manager
from tqdm import tqdm
from collections import Counter
import re

from src.model.EvaluateUrl import EvaluateUrl

class WebMiner:
    def __init__(self, start_url, max_urls=100, processes=8):
        self.start_url = start_url
        self.urls_to_visit = [self.start_url]
        self.max_urls = max_urls
        self.processes = processes
        self.manager = Manager()
        self.visited = self.manager.list([start_url])
        self.pool = Pool(processes=self.processes)
        self.pages_data = []

    @staticmethod
    def fetch_page_data(url):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            tags = ['p', 'span', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
            text_elements = []

            for tag in tags:
                text_elements.extend([element.get_text() for element in soup.find_all(tag)])

            links = [a['href'] for a in soup.find_all('a', href=True) if 'http' in a['href'] and not a['href'].endswith(('.jpg', '.png', '.gif'))]

            text_content = ' '.join(text_elements)
            return EvaluateUrl(url, body=text_content)
            #return {'url': url, 'text_content': text_content, 'links': links}

        except requests.exceptions.Timeout:
            print(f"Request to {url} timed out.")
            return []#{'url': url, 'text_content': '', 'links': []}

    @staticmethod
    def worker(self, args):
        results = []
        url, visited = args
        if is_valid_regex(url):
            data = self.fetch_page_data(url)
            links, text_content = data['links'], data['text_content']
            results = [link for link in links if link not in visited], {'url': url, 'text_content': text_content}
        return results
    
    def mine(self):

        with tqdm(total=self.max_urls) as pbar:
            while self.urls_to_visit and len(self.visited) < self.max_urls:
                results = self.pool.starmap(self.worker, [(url, self.visited) for url in self.urls_to_visit])
                new_urls = [link for result in results for link in result[0] if link not in self.visited]
                self.pages_data.extend([result[1] for result in results])
                self.visited.extend(new_urls)
                self.urls_to_visit = new_urls
                pbar.update(len(new_urls))

        self.pool.close()
        self.pool.join()

        for page in self.pages_data:
            page['most_common_words'] = self.most_common_words(page['text_content'])

        return self.pages_data

def is_valid_regex(http: str):
    url_regex = re.compile(
        r'^(https?://)'  # http or https
        r'([a-zA-Z0-9.-]+)'  # domain name
        r'(\.[a-zA-Z]{2,6})'  # top-level domain
        r'([/a-zA-Z0-9.-]*)*'  # path
        r'/?$'  # end of string
    )
    return bool(url_regex.match(http))

@staticmethod
def most_common_words(text):
    word_count = Counter(text.split())
    stopwords = set(['the', 'and', 'a', 'to', 'of', 'in', 'that', 'is', 'for', 'on', 'with', 'as', 'it', 'are', 'was', 'at', 'be', 'by', 'this', 'an'])
    filtered_words = {word: count for word, count in word_count.items() if word.lower() not in stopwords}
    return Counter(filtered_words).most_common(10)
