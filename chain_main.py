#!/usr/bin/env python

from multiprocessing import Queue, Process

from chain.control.light_server import light_server
from chain.control.main import parse_config, main

if __name__ == '__main__':
    wq = Queue()
    rq = Queue()
    app = light_server(rq, wq)
    config = parse_config()
    chain = Process(target=main, args=(config, wq, rq))
    chain.start()
    server = Process(target=app.run, kwargs={'port': 3600, 'host': '0.0.0.0'})
    server.start()
    while True:
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            chain.terminate()
            chain.join()
            server.terminate()
            server.join()
            break

