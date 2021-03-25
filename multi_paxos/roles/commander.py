"""Commander role"""

from ..parliament.role import Role

from ..constants.const import ACCEPT_RETRANSMIT
from ..constants.message_types import \
    ACCEPT, \
    PREEMPTED, \
    DECIDED, \
    DECISION

class Commander(Role):
    """Commander Role - Performs the Accept / Accepted portion of Multi-Paxos on behalf of the current Leader

    Responsible for sending and resending Accept messages, waiting for an Acceptor majority OR preemption

    When Proposal accepted, broadcasts a Decision message to all Nodes
    Response to Leader with Decided OR Preempted
    """

    def __init__(self, node, ballot_num, slot, proposal, peers):
        super(Commander, self).__init__(node)

        self.ballot_num = ballot_num
        self.slot = slot
        self.proposal = proposal
        self.acceptors = set([])
        self.peers = peers
        self.quorum = len(peers) / 2 + 1

    def start(self):
        self.node.send(set(self.peers) - self.acceptors, ACCEPT(
            slot=self.slot,
            ballot_num=self.ballot_num,
            proposal=self.proposal
        ))
        self.set_timer(ACCEPT_RETRANSMIT, self.start)

    def finished(self, ballot_num, preempted):
        if preempted:
            self.node.send([self.node.addr], PREEMPTED(
                slot=self.slot,
                preempted_by=ballot_num
            ))

        else:
            self.node.send([self.node.addr], DECIDED(
                slot=self.slot
            ))

        self.stop()

    def proc_accepted(self, sender, slot, ballot_num):
        if slot != self.slot:
            return
        # not preempted, decision can now be tendered
        if ballot_num == self.ballot_num:
            self.acceptors.add(sender)

            if len(self.acceptors) < self.quorum:
                return

            self.node.send(self.peers, DECISION(
                slot=self.slot,
                proposal=self.proposal
            ))

            self.finished(ballot_num, False)

        else:
            self.finished(ballot_num, True)
