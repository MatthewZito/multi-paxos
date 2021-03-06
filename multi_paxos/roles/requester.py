"""Requester Role"""
import itertools

from ..parliament.role import Role

from ..constants.const import INVOKE_RETRANSMIT
from ..constants.message_types import INVOKE

class Requester(Role):
    """Requester Role - Requests distributed state machine operations

    Responsible for managing requests to the distributed state machine

    The Requester sends Invoke messages to the local Replica
    until it receives a corresponding Invoked response
    """
    client_ids = itertools.count(start=100000)


    def __init__(self, node, n, cb):
        super(Requester, self).__init__(node)

        self.client_id = next(self.client_ids)
        self.n = n
        self.output = None
        self.cb = cb

    def start(self):
        self.node.send([self.node.addr], INVOKE(
            caller=self.node.addr,
            client_id=self.client_id,
            input_value=self.n
        ))

        self.invoke_timer = self.set_timer(INVOKE_RETRANSMIT, self.start)

    def proc_invoked(self, sender, client_id, output):
        if client_id != self.client_id:
            return

        self.logger.debug(
            f'Received output {output}'
        )

        self.invoke_timer.cancel()
        self.cb(output)
        self.stop()
