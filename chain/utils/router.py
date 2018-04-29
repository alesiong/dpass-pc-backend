from functools import wraps

import rlp

from chain.utils.multiplexer import Multiplexer

registered = {}


def route(tag):
    if isinstance(tag, str):
        tag = tag.encode()

    def __decorator(func):
        @wraps(func)
        def __wrapper(msg):
            args = rlp.decode(msg)
            try:
                if isinstance(args, list):
                    r = func(*args)
                elif args == b'':
                    r = func()
                else:
                    r = func(args)
            except TypeError:
                return rlp.encode(b'')
            if r is not None:
                return rlp.encode(r)

        registered[tag] = __wrapper

        return __wrapper

    return __decorator


def register(mx: Multiplexer):
    for tag, func in registered.items():
        mx.register(tag, func)
