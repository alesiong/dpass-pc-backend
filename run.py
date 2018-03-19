#!/usr/bin/env python
import argparse
import webbrowser
from multiprocessing import Process, Queue
from threading import Thread

import subprocess

from app import create_app
from app.utils.misc import get_os, get_executable
from app.utils.session_key import SessionKey

processes = {}
queue = Queue(5)


def main():
    parser = argparse.ArgumentParser(description='DPass - Distributed & Decentralized Password Manager')
    parser.add_argument('--develop', action='store_true', help='Run on development config.')
    parser.add_argument('--use_ethereum', action='store_true', help='Launch Ethereum (geth)')
    args = parser.parse_args()
    app = create_app('development' if args.develop else 'production', queue,
                     'ethereum' if args.use_ethereum else 'local')
    os = get_os()
    if os == 'win32':
        print('Windows 32-bit is not supported.')
        exit(1)

    if os.startswith('win'):
        server = Thread(target=app.run, kwargs={'use_reloader': False}, daemon=True)
    else:
        server = Process(target=app.run, kwargs={'use_reloader': False})

    if args.use_ethereum:
        processes['geth'] = subprocess.Popen([get_executable('./geth', 'geth'),
                                              '--datadir',
                                              './ethereum_private/data/',
                                              '--ethash.dagdir',
                                              './ethereum_private/data/ethash',
                                              '--networkid',
                                              '1042',
                                              '--targetgaslimit',
                                              '4000000'
                                              ],
                                             stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL)

    init_key = SessionKey.generate_key()
    queue.put(init_key)

    processes['server'] = server
    server.start()
    webbrowser.open_new_tab('http://localhost:5000/?key=' + init_key)


def terminate():
    if isinstance(processes['server'], Process):
        # FIXME: may change to terminate server gently
        processes['server'].terminate()
        processes['server'].join()
    if 'geth' in processes:
        processes['geth'].terminate()
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
