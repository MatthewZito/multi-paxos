import functools
import itertools
import logging

from ..utils.simulacron import SimulacronLogger

"""Base Node class"""

class Node():
    """Representative of a single node on the clustered Synod network.
    """

    # yield unique ids in case that constructor does not recv one
    unique_ids = itertools.count()

    def __init__(self, network, addr):
        self.network = network

        # if we don't recv an addr, generate the next unique id and assign
        self.addr = addr or 'NODE_%d' % next(self.unique_ids)
        # initialize simulation and logging
        self.logger = SimulacronLogger(
            logging.getLogger(self.addr),
            { 'network': self.network }
        )
        self.logger.info('initializing')
        self.roles = []
        # prepare a send method for future invocation
        self.send = functools.partial(
            self.network.send,
            self
        )

    def register(self, roles):
        """Register the given roles for this Synod round

        Args:
            roles
        """
        self.roles.append(roles)

    def unregister(self, roles):
        """Unregister the given roles

        Args:
            roles
        """
        self.roles.remove(roles)

    def recv(self, sender, message):
        """Process the reception of protocol messages and the execution thereof

        Args:
            sender: sender instance's addr
            message (namedtuple): message object containing ballot data
        """
        handler_name = 'proc_%s' % type(message).__name__

        for comp in self.roles[:]:
            if not hasattr(comp, handler_name):
                continue

            comp.logger.debug(f'received {message} from {sender}')

            fn = getattr(comp, handler_name)

            fn(
                sender=sender,
                **message._asdict()
            )
