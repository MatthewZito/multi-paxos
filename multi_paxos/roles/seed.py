"""Seed Role"""

from .initializer import Initializer

from ..parliament.role import Role

from ..constants.const import JOIN_RETRANSMIT
from ..constants.message_types import WELCOME

class Seed(Role):
    """Seed Role - Creates a new cluster

    Responsible for emulating a Replica and seeding a cluster

    Seed waits until it has received a Join message from a peer majority,
    then responds with a Welcome - accompanied by an initial state for the machine,
    and an empty set of Decisions)

    Finally, Seed stops itself and initializes an Initializer Role Node to join the
    newly-seeded cluster

    Seed mitigates disparities caused by sudden network partitions
    """

    def __init__(self, node, initial_state, executor, peers, initializer_gen=Initializer):
        super(Seed, self).__init__(node)

        self.initial_state = initial_state
        self.executor = executor
        self.peers = peers
        self.initializer_gen = initializer_gen
        self.witnessed_peers = set([])
        self.exit_timer = None

    def proc_join(self, sender):
        self.witnessed_peers.add(sender)

        if len(self.witnessed_peers) <= len(self.peers) / 2:
            return

        # cluster is now ready; welcome all peers
        self.node.send(list(self.witnessed_peers), WELCOME(
            state=self.initial_state,
            slot=1,
            decisions={}
        ))

        # wait for any straggler Joins
        if self.exit_timer:
            self.exit_timer.cancel()

        self.exit_timer = self.set_timer(JOIN_RETRANSMIT * 2, self.finish)

    def finish(self):
        """Initialize the node into the cluster that was just seeded
        Stop self once new genesis node is initialized
        """
        genesis = self.initializer_gen(
            self.node,
            peers=self.peers,
            executor=self.executor
        )

        genesis.start()
        self.stop()
