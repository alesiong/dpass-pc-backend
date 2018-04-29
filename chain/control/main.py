import argparse
import json
import logging
import os
import signal
import sys
from multiprocessing import Queue
from pathlib import Path

import gevent
from coincurve import PrivateKey

from chain.config import Config
from chain.control.command_server import *
from chain.network.chain_service import ChainService
from chain.state import State
from chain.storage import Storage
from chain.utils import Singleton
from chain.utils.multiplexer import Multiplexer
from p2p.app import BaseApp
from p2p.node_discovery.service import NodeDiscovery
from p2p.peer_manager.service import PeerManager
from p2p.utils import update_config_with_defaults


class DPChainApp(BaseApp, metaclass=Singleton):
    def __init__(self, config=None):
        assert config is not None
        super(DPChainApp, self).__init__(config)

    def stop(self):
        super(DPChainApp, self).stop()
        try:
            Multiplexer().stop()
        except AssertionError:
            pass
        Miner().stop()
        Miner().kill()


def parse_config():
    parser = argparse.ArgumentParser(description='DPass Chain - Blockchain application for DPass')
    parser.add_argument('--config', '-c',
                        help='Path of config file, default=`$data/config.json`')
    parser.add_argument('--data', '-d', default='./chain-data',
                        help='Path of data directory, default=`./chain-data`')
    parser.add_argument('--port', '-p', default=3500,
                        help='Listening port of the chain')
    parser.add_argument('--bootstrap', default='',
                        help='Bootstrap nodes with format `dpchain://key@host:port`, split with comma')
    args = parser.parse_args()

    directory = Path(args.data)
    directory.mkdir(parents=True, exist_ok=True)

    config_file = args.config or args.data + '/config.json'

    if len(args.bootstrap) == 0:
        bootstraps = []
    else:
        bootstraps = args.bootstrap.replace(' ', '').split(',')

    if os.path.exists(config_file):
        new_config = json.load(open(config_file))
    else:
        new_config = {}

    config = Config()
    config.update_data(args.data)
    config.update_port(args.port)
    config.update_bootstrap(bootstraps)
    config = update_config_with_defaults(new_config, config.config)

    if len(config['bootstrap_nodes']) == 0:
        print('WARNING: No bootstrap servers', file=sys.stderr)

    return config


def main(config, input_queue: Queue = None, output_queue: Queue = None):
    # load node private key
    storage = Storage(config['data'])
    storage.init_load()
    state = State()
    node_key = state.node_key.to_hex()
    if 'privkey_hex' not in config['node']:
        config['node']['privkey_hex'] = node_key

    # start multiplexer
    try:
        mx = Multiplexer(input_queue, output_queue)
        router.register(mx)
        mx.start()
    except AssertionError:
        pass

    logging.basicConfig(level=logging.INFO)

    gevent.get_hub().SYSTEM_ERROR = BaseException  # (KeyboardInterrupt, SystemExit, SystemError)

    # create app
    app = DPChainApp(config)

    # register services
    NodeDiscovery.register_with_app(app)
    PeerManager.register_with_app(app)
    ChainService.register_with_app(app)

    # start app
    app.start()

    # wait for interupt
    evt = gevent.event.Event()
    # gevent.signal(signal.SIGQUIT, gevent.kill) ## killall pattern
    try:
        gevent.signal(signal.SIGQUIT, evt.set)
    except AttributeError:
        pass
    gevent.signal(signal.SIGTERM, evt.set)
    gevent.signal(signal.SIGINT, evt.set)

    evt.wait()

    # finally stop
    storage.store_state()
    app.stop()
