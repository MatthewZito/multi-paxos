import itertools
import functools
import logging

from .constants import message_types, const

class SimulacronLogger(logging.LoggerAdapter):

    def process(self, message, kwargs):
        return 'T=%.4f %s' % (self.extra['network'].now, message), kwargs

    def get_child(self, name):
        return self.__class__(
            self.logger.get_child(name),
            { 'network': self.extra['network'] }
        )

class Role():

    def __init__(self, node):
        self.node = node
        self.node.register(self)
        self.running = True
        self.logger = node.logger.get_child(type(self).__name__)

    def set_timer(self, seconds, cb):
        return self.node.network.set_timer(
            self.node.addr,
            seconds,
            lambda: self.running and cb()
        )

    def stop(self):
        self.running = False
        self.node.unregister(self)


class Node():
    unique_ids = itertools.count()

    def __init__(self, network, addr):
        self.network = network
        self.addr = addr
        self.logger = SimulacronLogger(
            logging.getLogger(self.addr),
            { 'network': self.network }
        )
        self.logger.info('initializing')
        self.roles = []
        self.send = functools.partial(
            self.network.send,
            self
        )

    def register(self, roles):
        self.roles.append(roles)

    def unregister(self, roles):
        self.roles.remove(roles)

    def recv(self, sender, message):
        handler_name = f'do_{type(message).__name__}'

        for comp in self.roles[:]:
            if not hasattr(comp, handler_name):
                continue
            comp.logger.debug(f'received {message} from {sender}')

            fn = getattr(comp, handler_name)
            fn(
                sender=sender,
                **message._asdict()
            )

class Member(object):
    pass
