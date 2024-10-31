from WebMiner import WebMiner

if __name__ == '__main__': 
    
    start_url = 'https://www.foxnews.com' 
    # Replace with your target URL 
    scraper = WebMiner(start_url) 
    result = scraper.mine() 

    for page in result: 
        print(f"URL: {page.url}") 
        print(f"Most Common Words: {page.most_common_words}") 
        print("-" * 40)

