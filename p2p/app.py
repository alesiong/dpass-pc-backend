from collections import UserDict

from p2p import utils
from p2p.log import get_logger
from p2p.service import BaseService

log = get_logger('app')


class BaseApp(object):
    default_config = dict(
        client_version_string='dpass-chain',
        deactivated_services=[],
        bootstrap_nodes=[])

    def __init__(self, config=default_config):
        self.config = utils.update_config_with_defaults(config,
                                                        self.default_config)
        self.services = UserDict()

    def register_service(self, service):
        """
        registers protocol with app, which will be accessible as
        app.services.<protocol.name> (e.g. app.services.p2p or app.services.eth)
        """
        assert isinstance(service, BaseService)
        assert service.name not in self.services
        log.info('registering service', service=service.name)
        self.services[service.name] = service
        setattr(self.services, service.name, service)

    def deregister_service(self, service):
        assert isinstance(service, BaseService)
        del self.services[service.name]
        delattr(self.services, service.name)

    def start(self):
        for service in self.services.values():
            service.start()

    def stop(self):
        for service in self.services.values():
            service.stop()

    def join(self):
        for service in self.services.values():
            service.join()
