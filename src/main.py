from WebMiner import WebMiner

if __name__ == '__main__':
    start_url = 'https://www.foxnews.com'
    miner = WebMiner(start_url)
    visited = miner.mine()

    [print(a.body) for a in visited[0:10]]