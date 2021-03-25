"""Initializer Role"""

import itertools

from .acceptor import Acceptor
from .commander import Commander
from .leader import Leader
from .replica import Replica
from .scout import Scout

from ..parliament.role import Role

from ..constants.const import JOIN_RETRANSMIT
from ..constants.message_types import JOIN

class Initializer(Role):
    """Initializer Role - Introduce a new Node to an extant cluster

    Responsible for induction of new Nodes joining the cluster

    Sends Join messages to ea peer until it receives a Welcome on behalf of the new Node
    """

    def __init__(self, node, peers, executor,
            replica_gen=Replica, acceptor_gen=Acceptor, leader_gen=Leader,
            commander_gen=Commander, scout_gen=Scout):

        super(Initializer, self).__init__(node)

        self.executor = executor
        self.peers = peers
        self.peers_cycle = itertools.cycle(peers)
        self.replica_gen = replica_gen
        self.acceptor_gen = acceptor_gen
        self.leader_gen = leader_gen
        self.commander_gen = commander_gen
        self.scout_gen = scout_gen

    def start(self):
        self.join()

    def join(self):
        self.node.send([next(self.peers_cycle)], JOIN())
        self.set_timer(JOIN_RETRANSMIT, self.join)

    def proc_welcome(self, sender, state, slot, decisions):
        """Initialize each role - with initial state - in the context of the inducted Node

        Args:
            sender
            state
            slot
            decisions
        """
        self.acceptor_gen(self.node)

        self.replica_gen(
            self.node,
            executor=self.executor,
            peers=self.peers,
            state=state,
            slot=slot,
            decisions=decisions
        )

        self.leader_gen(
            self.node,
            peers=self.peers,
            commander_gen=self.commander_gen,
            scout_gen=self.scout_gen
        ).start()

        self.stop()
