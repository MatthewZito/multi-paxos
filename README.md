## multi_paxos.py | A concise Python implementation of multi-paxos

## Introduction + About

*Paxos* - as described by Leslie Lamport in <ins>The Part Time Parliament</ins>, sub. 1990, pub. 1998 - is in its simplest form a means by which a distributed network of nodes can agree (achieve consensus) on a shared state. Multi-Paxos, then, concerns itself with consensus on a numbered sequence of state transitions.

This implementation utilizes a clustered network, dynamically assigning to its nodes the canonical Synod roles e.g. Proposer, Acceptor, Leader.

The roles and their respective responsibilities are:

- Acceptor: tenders Promises and accept Proposals
- Initializer: inducts new nodes into the existing cluster
- Leader: leads Multi-Paxos iterations by Accepting and tendering Decisions
- Replica: manages the distributed state machine core; submits Proposals; commits Decisions; responds to Requesters
- Requester: requests a distributed state machine transition
- Scout: dispatches Prepare, Promise messages on a Leader's behalf
- Seed: initializes a new cluster

You can find the roles' code in the [roles module](multi_paxos/roles). Each role is assigned to a node via dependency injection; this assignment is furthermore contingent on rules local to each role and conformant to the Multi-Paxos algorithm.

The core network over which the cluster communicates is a deterministic simulation (that is, it behaves exactly the same given the same genesis seed was provided). Message transmissions are scheduled via timers, managed by Python's internal `heapq`. Message scheduling for our purposes is implemented with a random delay in order to simulate packet loss and message propagation delay.

The entire system utilizes a logging class that pipes all messages being transmitted during the consensus ballots to stdout. Logs display the node, its current role, the message being transmitted, and the intended recipient. You can utilize this to test-run a simulation (see instructions in next section).

**Note** This implementation uses a deterministic simulation in lieu of an actual network, though the network component can be supplanted with a real network without consequence.

## Running a Simulation

To run a simulation:

```bash
python3 -m multi_paxos <seed: int>
```

Or pipe to a file:

```bash
python3 -m multi_paxos 6 &> out
```

Depending on your shell, you may need to strip the ANSI color codes using sed or remove them from `__main__.py`.

Quick sed one-liner:

```bash
sed -r "s/\\^\\[(\\[[^@-~]+[@-~]|[0-9@-_]|%@)//g"
```

See a sample simulation output [here](docs/simulation.txt)
