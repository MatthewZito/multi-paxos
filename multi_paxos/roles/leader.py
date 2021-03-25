"""Leader role"""

from ..parliament.role import Role

from ..constants.const import LEADER_TIMEOUT
from ..constants.message_types import \
    ACTIVE, \
    BALLOT

from .commander import Commander
from .scout import Scout

class Leader(Role):
    """Leader role

    Responsible for taking Propose messages requesting new ballots, and making decisions
    Active when a Prepare / Promise is successfully executed

    Active Leader may send Accept messages in response to Propose immediately
    """

    def __init__(self, node, peers, commander_gen=Commander, scout_gen=Scout):
        super(Leader, self).__init__(node)

        self.ballot_num = BALLOT(0, node.addr)
        self.active = False
        self.proposals = { }
        self.commander_gen = commander_gen
        self.scout_gen = scout_gen
        self.scouting = False
        self.peers = peers

    def start(self):
        # notify all other Nodes to inform that this Node is active prior to LEADER_TIMEOUT expiry
        def active():
            if self.active:
                self.node.send(self.peers, ACTIVE())
            self.set_timer(LEADER_TIMEOUT / 2.0, active)
        active()

    def spawn_scout(self):
        """Spawn new scout when Leader Node wants to become Active,
        in response to receiving a Propose while inactive
        """
        assert not self.scouting

        self.scouting = True
        self.scout_gen(
            self.node,
            self.ballot_num,
            self.peers
        ).start()

    def spawn_commander(self, ballot_num, slot):
        proposal = self.proposals[slot]
        self.commander_gen(
            self.node,
            ballot_num,
            slot,
            proposal,
            self.peers
        ).start()


    def proc_adopted(self, sender, ballot_num, accepted_proposals):
        self.scouting = False
        self.proposals.update(accepted_proposals)
        # do not respawn commanders if undecided proposals extant; replica will handle reproposal
        self.logger.info(
            'Leader initializing active state'
        )
        self.active = True

    def proc_preempted(self, sender, slot, preempted_by):
        if not slot: # from scount
            self.scouting = False

        self.logger.info(
            f'Leader preempted by {preempted_by.leader}'
        )

        self.active = False
        self.ballot_num = BALLOT(
            (preempted_by or self.ballot_num).n + 1,
            self.ballot_num.leader
        )

    def proc_propose(self, sender, slot, proposal):
        if slot not in self.proposals:
            if self.active:
                self.proposals[slot] = proposal

                self.logger.info(f'Spawning commander for slot {slot}')

                self.spawn_commander(self.ballot_num, slot)

            else:
                if not self.scouting:
                    self.logger.info(
                        f'Received Propose while not active; scouting...'
                    )
                    self.spawn_scout()

                else:
                    self.logger.info(
                        'Received Propose while scouting; ignored'
                    )

        else:
            self.logger.info('Received Propose for a slot already being proposed')
