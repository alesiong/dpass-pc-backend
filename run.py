#!/usr/bin/env python
import argparse
import webbrowser
from multiprocessing import Process, Queue

from app import create_app
from app.utils.session_key import SessionKey

processes = {}
queue = Queue(5)


def main():
    parser = argparse.ArgumentParser(description='DPass - Distributed & Decentralized Password Manager')
    parser.add_argument('--develop', action='store_true', help='Run on development config.')
    args = parser.parse_args()
    app = create_app('development' if args.develop else 'production', queue)
    server = Process(target=app.run, kwargs={'use_reloader': False})

    init_key = SessionKey.generate_key()
    queue.put(init_key)

    processes['server'] = server
    server.start()
    webbrowser.open_new_tab('http://localhost:5000/pages/demo/#key=' + init_key)
    print(init_key)


def terminate():
    processes['server'].terminate()
    processes['server'].join()
    queue.close()


if __name__ == '__main__':
    try:
        main()
        while True:
            input()
            if not queue.empty():
                print(queue.get())
    except (EOFError, KeyboardInterrupt):
        terminate()
