from WebMiner import WebMiner
import tensorflow

if __name__ == '__main__': 
    
    start_url = 'https://www.foxnews.com/' 
    # Replace with your target URL 
    scraper = WebMiner(start_url) 
    result = scraper.mine() 

    print(result)

