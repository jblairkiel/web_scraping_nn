from WebMiner import WebMiner
import tensorflow

if __name__ == '__main__': 
    
    start_url = 'https://www.foxnews.com/' 
    #start_url = 'https://www.yahoo.com/' 
    #start_url = 'https://www.espn.com/' 
    # Replace with your target URL 
    scraper = WebMiner(start_url) 
    result = scraper.mine() 

    print(result)

