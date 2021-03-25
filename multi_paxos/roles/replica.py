"""Local Replica"""

from ..parliament.role import Role

from ..constants.const import LEADER_TIMEOUT
from ..constants.message_types import \
    PROPOSAL, \
    PROPOSE, \
    INVOKED, \
    WELCOME

class Replica(Role):
    """Local Replica

    Responsible for making new proposals, invoking the state machine upon proposal decisions,
    and tracking the current leader.

    Adds new nodes to the cluster.
    """

    def __init__(self, node, executor, state, slot, decisions, peers):
        super(Replica, self).__init__(node)

        self.executor = executor
        self.state = state
        self.slot = slot
        self.decisions = decisions
        self.peers = peers
        self.proposals = { }
        # next slot num for proposal, initialize at given
        self.next_slot = slot
        self.latest_leader = None
        self.latest_leader_timeout = None

    def proc_invoke(self, sender, caller, client_id, input_value):
        proposal = PROPOSAL(caller, client_id, input_value)

        slot = next(( s for s, p in self.proposals.items() if p == proposal), None)

        # propose, or repropose if this proposal already has a slot
        self.propose(proposal, slot)

    def propose(self, proposal, slot=None):
        """Send (or resend, if slot is specified) a proposal to the current leader

        Args:
            proposal
            slot    Defaults to None.
        """

        if not slot:
            # incr current, next slots
            slot, self.next_slot = self.next_slot, self.next_slot + 1

        self.proposals[slot] = proposal
        # find presumed leader - either latest known or self
        # which very well might invoke scout to elect self as leader
        leader = self.latest_leader or self.node.addr
        self.logger.info(
            f'Proposing {proposal} at slot {slot} to leader {leader}'
        )

        self.node.send([leader], PROPOSE(
            slot=slot,
            proposal=proposal
        ))

    def proc_decision(self, sender, slot, proposal):
        assert not self.decisions.get(self.slot, None), 'next slot to commit is already decided'

        if slot in self.decisions:
            assert self.decisions[slot] == proposal, f'slot {slot} already decided with {self.decisions[slot]}'
            return

        self.decisions[slot] = proposal
        self.next_slot = max(self.next_slot, slot + 1)

        # repropose in new slot if slot was lost and was not a noop
        reproposal = self.proposals.get(slot)

        if (reproposal is not None and
            reproposal != proposal and
            reproposal.caller
            ):
            self.propose(reproposal)

        # execute pending, decided proposals
        while True:
            commit_proposal = self.decisions.get(self.slot)

            if not commit_proposal:
                break # no decision yet
            commit_slot, self.slot = self.slot, self.slot + 1

            self.commit(commit_slot, commit_proposal)

    def commit(self, slot, proposal):
        """Commit a proposal that is decided and in-sequence

        Args:
            slot
            proposal
        """

        decided_proposals = [p for s, p in self.decisions.items() if s < slot]

        # duplicate
        if proposal in decided_proposals:
            self.logger.info(
                f'Not committing duplicate proposal {proposal} at slot {slot}'
            )
            return

        self.logger.info(
            f'Committing {proposal} at slot {slot}'
        )

        if proposal.caller is not None:
            # perform client op
            self.state, output = self.executor(self.state, proposal.input)
            self.node.send([proposal.caller], INVOKED(
                client_id=proposal.client_id,
                output=output
            ))

    # leader tracking

    def proc_adopted(self, sender, ballot_num, accepted_proposals):
        self.latest_leader = self.node.addr
        self.leader_alive()

    def proc_accepting(self, sender, leader):
        self.latest_leader = leader
        self.leader_alive()

    def proc_active(self, sender):
        if sender != self.latest_leader:
            return
        self.leader_alive()

    def leader_alive(self):
        if self.latest_leader_timeout:
            self.latest_leader_timeout.cancel()

        def reset_leader():
            idx = self.peers.index(self.latest_leader)
            self.latest_leader = self.peers[(idx + 1) % len(self.peers)]

            self.logger.debug(
                f'Leader timed out; presumed dead. Attempting next: {self.latest_leader}'
            )

            self.latest_leader_timeout = self.set_timer(LEADER_TIMEOUT, reset_leader)

        # cluster induction

        def proc_join(self, sender):
            if sender in self.peers:
                self.node.send([sender], WELCOME(
                    state=self.state,
                    slot=self.slot,
                    decisions=self.decisions
                ))
