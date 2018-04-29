class Config:
    def __init__(self):
        self.__config = {
            "capabilities": {
                "miner": True,
                "bootstrap": True,
                "lightserver": False,
                "chainnode": True
            },
            "listen_host": "0.0.0.0",
            "listen_port": 3500,
            "bootstrap_nodes": [],
            "p2p": {
                "min_peers": 2
            },
            "data": "./chain-data",
            "node": {}
        }

    def update_port(self, port):
        self.__config['listen_port'] = int(port)

    def update_bootstrap(self, bootstraps):
        if len(bootstraps) == 0:
            return
        self.__config['bootstrap_nodes'] = bootstraps

    def update_node_key(self, node_key):
        self.__config['node']['privkey_hex'] = node_key

    def update_data(self, data):
        self.__config['data'] = data

    @property
    def config(self):
        return self.__config
