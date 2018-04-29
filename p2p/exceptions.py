import atexit


class DefectiveMessage(Exception):
    pass


class InvalidSignature(DefectiveMessage):
    pass


class WrongMAC(DefectiveMessage):
    pass


class PacketExpired(DefectiveMessage):
    pass


class ProtocolError(Exception):
    pass


class SubProtocolError(ProtocolError):
    pass


class PeerErrorsBase(object):
    def add(self, address, error, client_version=''):
        pass


class PeerErrors(PeerErrorsBase):
    def __init__(self):
        self.errors = dict()  # node: ['error',]
        self.client_versions = dict()  # address: client_version

        def report():
            for k, v in self.errors.items():
                print(k, self.client_versions.get(k, ''))
                for e in v:
                    print('\t', e)

        atexit.register(report)

    def add(self, address, error, client_version=''):
        self.errors.setdefault(address, []).append(error)
        if client_version:
            self.client_versions[address] = client_version


class UnknownCommandError(Exception):
    "raised if we recive an unknown command for a known protocol"
    pass


class MultiplexerError(Exception):
    pass


class DeserializationError(MultiplexerError):
    pass


class FormatError(MultiplexerError):
    pass


class ECIESDecryptionError(RuntimeError):
    pass
