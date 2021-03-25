"""Scout role"""

from ..parliament.role import Role

from ..constants.const import PREPARE_RETRANSMIT
from ..constants.message_types import \
    ADOPTED, \
    PREEMPTED, \
    PREPARE

class Scout(Role):
    """Scout Role - Perform the Prepare / Promise portion of Multi-Paxos on behalf of the Leader

    Responsible for sending (and resending, if needed) a Prepare

    Collects Promise responses until a majority of peers have replied OR the Scout has been preempted

    Communicates with Leader via Adopted (majority consensus) or Preempted (preempted)
    """

    def __init__(self, node, ballot_num, peers):
        super(Scout, self).__init__(node)

        self.ballot_num = ballot_num
        self.accepted_proposals = { }
        self.acceptors = set([])
        self.peers = peers
        self.quorum = len(peers) / 2 + 1
        self.retransmit_timer = None

    def start(self):
        self.logger.info('Scout initialized')
        self.send_prepare()


    def send_prepare(self):
        self.node.send(self.peers, PREPARE(
            ballot_num=self.ballot_num
        ))
        self.retransmit_timer = self.set_timer(PREPARE_RETRANSMIT, self.send_prepare)

    def update_accepted(self, accepted_proposals):
        acc = self.accepted_proposals
        for slot, (ballot_num, proposal) in accepted_proposals.items():
            if slot not in acc or acc[slot][0] < ballot_num:
                acc[slot] = (ballot_num, proposal)

    def proc_promise(self, sender, ballot_num, accepted_proposals):
        if ballot_num == self.ballot_num:
            self.logger.info(
                f'Received matching Promise; require {self.quorum}'
            )

            self.update_accepted(accepted_proposals)
            self.acceptors.add(sender)

            if len(self.acceptors) >= self.quorum:
                # strip ballot nums from local accepted_proposals given it now represents a majority
                accepted_proposals = dict((s, p) for s, (b, p) in self.accepted_proposals.items())
                # Node is now adopted - does NOT mean no other leader is active;
                # possible conflicts will be handled by Commanders
                self.node.send([self.node.addr], ADOPTED(
                    accepted_proposals=accepted_proposals
                ))

                self.stop()

        else:
            # the acceptor has promised another leader a higher ballot num
            self.node.send([self.node.addr], PREEMPTED(
                slot=None,
                preempted_by=ballot_num
            ))

            self.stop()
