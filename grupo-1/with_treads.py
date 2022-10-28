import threading
import queue
import time
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup

#url fatects
base_url="http://localhost:8080"
fatecs_url=f"{base_url}/listafatecs.json"
q = queue.Queue()
session = FuturesSession(max_workers=20)

fatecs = []

def parse_fatecs(content):
    fatecs.append()
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
tread = threading.Thread(target=worker, daemon=True)
tread.start()
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
