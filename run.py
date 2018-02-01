import argparse
import subprocess
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

    # TODO: change the path of `geth`
    geth = subprocess.Popen(['geth',
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
