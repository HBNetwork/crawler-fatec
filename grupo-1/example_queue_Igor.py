import queue
import random
import threading
import time

def worker(q, multiplicity=5, maxlevel=3, lock=threading.Lock()):
    for task in iter(q.get, None):  # blocking get until None is received
        try:
            if len(task) < maxlevel:
                for i in range(multiplicity):
                    q.put(task + str(i))  # schedule the next level
            time.sleep(random.random())  # emulate some work
            with lock:
                print(task)
        finally:
            q.task_done()

worker_count = 2
q = queue.LifoQueue()
threads = [threading.Thread(target=worker, args=[q], daemon=True)
           for _ in range(worker_count)]
for t in threads:
    t.start()

for task in "01234":  # populate the first level
    q.put(task)
    q.join()  # block until all spawned tasks are done
for _ in threads:  # signal workers to quit
    q.put(None)
for t in threads:  # wait until workers exit
    t.join()