"""Acceptor Role"""

from ..parliament.role import Role

from ..constants.const import NULL_BALLOT
from ..constants.message_types import \
    ACCEPTING, \
    PROMISE, \
    ACCEPTED

class Acceptor(Role):
    """Acceptor Role - Makes Promises and accepts Proposals

    Manages acceptance of ballots

    Stores ballot number of most recent Promise, along with accepted proposals for ea slot
    Response to Prepare and Accept messages.
    """

    def __init__(self, node):
        super(Acceptor, self).__init__(node)
        self.ballot_num = NULL_BALLOT
        self.accepted_proposals = { }

    def proc_prepare(self, sender, ballot_num):
        """Process a Prepare message

        Args:
            sender: The origin Node of the Accept message
            ballot_num: Accept message ballot no.
        """

        # always accept higher num, never lower
        if ballot_num > self.ballot_num:
            self.ballot_num = ballot_num
            # available for new leader
            self.node.send([self.node.addr], ACCEPTING(leader=sender))

        self.node.send([sender], PROMISE(
            ballot_num=self.ballot_num,
            accepted_proposals=self.accepted_proposals
        ))

    def proc_accept(self, sender, ballot_num, slot, proposal):
        """Process an Accept message

        Args:
            sender: The origin Node of the Accept message
            ballot_num: Accept message ballot no.
            slot
            proposal
        """
        if ballot_num >= self.ballot_num:
            self.ballot_num = ballot_num

            acc = self.accepted_proposals

            if slot not in acc or acc[slot][0] < ballot_num:
                acc[slot] = (ballot_num, proposal)

        self.node.send([sender], ACCEPTED(
            slot=slot,
            ballot_num=self.ballot_num
        ))
