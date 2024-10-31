
from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool, Manager
from tqdm import tqdm
import re
from collections import Counter

from model.EvaluateUrl import EvaluateUrl
class WebMiner():
    
    def __init__(self, start_url: str):
        self.max_urls = 100
        self.manager = Manager()
        _start_url = EvaluateUrl(start_url, "")
        self.visited = self.manager.list([_start_url])
        
        self.pool = Pool(processes=4)
        self.urls_to_visit = [start_url]
    
    def collect_html_bodies(self, url: str):
        response = requests.get(url) 
        soup = BeautifulSoup(response.content, 'html.parser') 
        # Extract text from common text tags 
        tags = ['p', 'span', 'div', 'li'] 
        text_elements = [] 
        for tag in tags: 
            text_elements.extend([element.get_text() for element in soup.find_all(tag)]) 
        
        # Combine the text and use a counter to find the most common words 
        text = ' '.join(text_elements) 
        word_list = text.split() 
        word_count = Counter(word_list) 
        
        # Filter out common stopwords (you can expand this list) 
        stopwords = set(['the', 'and', 'a', 'to', 'of', 'in', 'that', 'is', 'for', 'on', 'with', 'as', 'it', 'are', 'was', 'at', 'be', 'by', 'this', 'an']) 
        filtered_words = {word: count for word, count in word_count.items() if word.lower() not in stopwords} 
        
        # Get the top 10 most common words 
        most_common_words = Counter(filtered_words).most_common(10) 
        return most_common_words
    
    def find_links(self, url):
        links = []
        try:
            response = requests.get(url, timeout=10)
        except Exception as ex:
            print(f"Error visiting: {url}")
            return links
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'http' in href and not href.endswith(('.jpg', '.png', '.gif')):
                    body = self.collect_html_bodies(href)
                    links.append(EvaluateUrl(href, body))
        return links

    def is_valid_regex(self, http: str):
        url_regex = re.compile(
            r'^(https?://)'  # http or https
            r'([a-zA-Z0-9.-]+)'  # domain name
            r'(\.[a-zA-Z]{2,6})'  # top-level domain
            r'([/a-zA-Z0-9.-]*)*'  # path
            r'/?$'  # end of string
        )
        return bool(url_regex.match(http))

    def worker(self, args):
        url, visited = args
        if self.is_valid_regex(url):
            links = self.find_links(url)
            return [link for link in links if link not in visited]
        else:
            return []

    def mine(self):
        
        with tqdm(total=100) as pbar:
            while self.urls_to_visit and len(self.visited) < self.max_urls:
                results = self.pool.map(self.worker, [(url, self.visited) for url in self.urls_to_visit])
                visited_links = [str(link) for link in self.visited]
                new_urls = [link for links in results for link in links if link not in visited_links]
                self.visited.extend(new_urls)
                urls_to_visit = new_urls
                pbar.update(len(urls_to_visit))

        self.pool.close()
        self.pool.join()
        return self.visited

