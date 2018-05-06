import gevent
from gevent.server import DatagramServer

from p2p.log import get_logger
from p2p.node_discovery.protocol import DiscoveryProtocol
from p2p.node_discovery.utils import Address, Node
from p2p.service import BaseService

log = get_logger('node_discovery.service')


class NodeDiscovery(BaseService):
    """
    Persist the list of known nodes with their reputation
    """

    name = 'discovery'
    server = None  # will be set to DatagramServer
    nat_upnp = None
    default_config = dict(
        discovery=dict(bootstrap_nodes=[]),
        node=dict(privkey_hex=''))

    def __init__(self, app):
        BaseService.__init__(self, app)
        log.info('NodeDiscovery init')

        if not self.app.config['discovery']['bootstrap_nodes']:
            self.app.config['discovery']['bootstrap_nodes'] = self.app.config[
                'bootstrap_nodes']

        # man setsockopt
        self.protocol = DiscoveryProtocol(app=self.app, transport=self)

    @property
    def address(self):
        ip = self.app.config['listen_host']
        port = self.app.config['listen_port']
        return Address(ip, port)

    def send(self, address, message):

        assert isinstance(address, Address)
        log.debug('sending', size=len(message), to=address)
        try:
            self.server.sendto(message, (address.ip, address.udp_port))
        except gevent.socket.error as e:
            log.error('udp write error', address=address, errno=e.errno,
                      reason=e.strerror)
            log.error('waiting for recovery')
            gevent.sleep(0.5)

    def receive(self, address, message):
        assert isinstance(address, Address)
        self.protocol.receive(address, message)

    def _handle_packet(self, message, ip_port):
        try:
            log.debug('handling packet', address=ip_port, size=len(message))
            assert len(ip_port) == 2
            address = Address(ip=ip_port[0], udp_port=ip_port[1])
            self.receive(address, message)
        except Exception as e:
            log.error("failed to handle discovery packet",
                      error=e, message=message, ip_port=ip_port)
            log.exception(e)

    def start(self):
        log.info('starting discovery')
        # start a listening server
        ip = self.app.config['listen_host']
        port = self.app.config['listen_port']
        # nat port mappin
        # self.nat_upnp = add_portmap(port, 'UDP', 'Ethereum DEVP2P Discovery')
        log.info('starting listener', port=port, host=ip)
        self.server = DatagramServer((ip, port), handle=self._handle_packet)
        self.server.start()
        super(NodeDiscovery, self).start()

        # bootstap
        nodes = [Node.from_uri(x) for x in
                 self.app.config['discovery']['bootstrap_nodes']]
        if nodes:
            self.protocol.kademlia.bootstrap(nodes)

    def _run(self):
        log.debug('_run called')
        evt = gevent.event.Event()
        evt.wait()

    def stop(self):
        log.info('stopping discovery')
        # remove_portmap(self.nat_upnp,
        #                self.app.config['discovery']['listen_port'], 'UDP')
        if self.server:
            self.server.stop()
        super(NodeDiscovery, self).stop()


class PatchedDatagramServer(DatagramServer):
    def do_read(self):
        try:
            return super(PatchedDatagramServer, self).do_read()
        except ConnectionResetError:
            return
