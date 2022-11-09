import threading
import queue
import re
import requests


def processa_a(payload, *args):
    return [("http://httpbin.org"+url, processa_b) for url in re.findall(r"href='(.+?)'", payload)]


def processa_b(payload, *args):
    return [("http://httpbin.org"+url, processa_c) for url in re.findall(r"href='(.+?)'", payload)]

def processa_c(payload, tid):
    print(tid, re.findall(r"\s(\d+?)\s", payload))
    return []


def download(tid, q, timeout=5):
    try:
        while True:
            url, callback = q.get(timeout=timeout)
            r = requests.get(url)
            for t in callback(r.text, tid):
                q.put(t)
    except queue.Empty:
        print(f"Finishing {tid}")


def run(task, q, workers=20, timeout=5, daemon=True):
    threads = [threading.Thread(target=task, args=[n, q, timeout], daemon=daemon)
           for n in range(workers)]
    for t in threads: t.start()
    for t in threads: t.join()


if __name__ == "__main__":
    q = queue.Queue()
    q.put((f"http://httpbin.org/links/20/0", processa_a))
    run(download, q)
    
