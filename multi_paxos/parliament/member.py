"""Base Parliamentary Member class"""

import queue
import threading

from ..roles.initializer import Initializer
from ..roles.requester import Requester
from ..roles.seed import Seed

class Member():
    """Initializer for each cluster member (node).

    Provides a localized state machine and list of peers.
    Adds a boostrap role to the node if joining an existing cluster, else a seed if creating a new one.

    Executes the protocol (`Network.run`) on a discrete thread.
    """

    def __init__(self, state_machine, network,
        peers, seed=None, seed_gen=Seed,
        init_gen = Initializer
    ):
        self.network = network
        self.node = network.new_node()

        if seed is not None:
            self.startup_role = seed_gen(
                self.node,
                initial_state=seed,
                peers=peers,
                executor=state_machine
            )
        else:
            self.startup_role = init_gen(
                self.node,
                executor=state_machine,
                peers=peers
            )

        self.requester = None


    def start(self):
        """Initialize the network protocol on a discrete thread
        """
        self.startup_role.start()
        self.thread = threading.Thread(target=self.network.run)
        self.thread.start()

    def invoke(self, input_value, requester_gen=Requester):
        """Invokes the proposal for a state transition

        Return the results upon a given proposal reaching a decided state
        Awaits a synchronized queue for the result from the protocol thread

        Args:
            input_value:
            requester ([type], optional): Defaults to Requester.

        Returns:
            State machine output
        """
        assert self.requester is None

        q = queue.Queue()

        self.requester = requester_gen(
            self.node,
            input_value,
            q.put
        )

        out = q.get()
        self.requester = None
        return out
