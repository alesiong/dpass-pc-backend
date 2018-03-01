from app.utils.ethereum_storage import EthereumStorage
from app.utils.misc import get_env
import time

def synchronization():
    account = get_env()['ETH_ACC']
    password = get_env()['ETH_PASS']
    while True:
        storage = EthereumStorage(account, password)
        storage.store()

        # TODO: may need to sync into local database? but how?

        # FIXME: how to decide the time interval?
        time.sleep(1800)


