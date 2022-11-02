import threading
import queue
import time
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup
import requests

#url fatects
base_url="http://localhost:8080"
fatecs_url=f"{base_url}/listafatecs.json"
q = queue.Queue()
session = FuturesSession(max_workers=20)

fatecs = []

def parse_fatecs(content):
    fatecs.append(content)
    return content

def worker():
    while True:
        item = q.get()
        print(f'Working on {item}')
        # future
        url = item.get('url')
        data = item.get('data')
        parse = item.get('parse')
        if data:
            # POST
            response = session.post(url, data=data)
        else:
            # GET
            response = session.get(url)

        q.put(parse(response))
        
        print(f'Finished {lista_fatecs}')
        q.task_done()

# Turn-on the worker thread.
# Send thirty task requests to the worker.
# for item in range(30):
#     q.put(item)
item = {
    'url': fatecs_url,
    'parse': parse_fatecs,
}
q.put(item)

# Block until all tasks are done.
q.join()
print('All work completed')

import re
import requests


def processa_a(payload):
    return [(url, processa_b) for url in re.findall(r"href='(.+?)'", payload)]


def processa_b(payload):
    print(payload)
    return []


def download(q):
    while True:
        url, callback = q.get()
        r = requests.get(url)
        for t in callback(r):
            queue.put(t)

if __name__ == "__main__":
    q.put((f"http://httpbin.org/links/10/0", processa_a))
    tread = threading.Thread(target=download)
    tread.start()
    

