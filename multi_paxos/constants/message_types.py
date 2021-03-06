"""Multi-Paxos Algorithm Message Types"""

from collections import namedtuple

ACCEPTED = namedtuple('accepted', [ 'slot', 'ballot_num' ])
ACCEPT = namedtuple('accept', [ 'slot', 'ballot_num', 'proposal' ])
DECISION = namedtuple('decision', [ 'slot', 'proposal' ])
INVOKED = namedtuple('invoked', [ 'client_id', 'output' ])
INVOKE = namedtuple('invoke', [ 'caller', 'client_id', 'input_value' ])
JOIN = namedtuple('join', [ ])
ACTIVE = namedtuple('active', [ ])
PREPARE = namedtuple('prepare', [ 'ballot_num' ])
PROMISE = namedtuple('promise', [ 'ballot_num', 'accepted_proposals' ])
PROPOSE = namedtuple('propose', [ 'slot', 'proposal' ])
WELCOME = namedtuple('welcome', [ 'state', 'slot', 'decisions' ])
DECIDED = namedtuple('decided', [ 'slot' ])
PREEMPTED = namedtuple('preempted', [ 'slot', 'preempted_by' ])
ADOPTED = namedtuple('adopted', [ 'ballot_num', 'accepted_proposals' ])
ACCEPTING = namedtuple('accepting', [ 'leader' ])

PROPOSAL = namedtuple('proposal', [ 'caller', 'client_id', 'input' ])
BALLOT = namedtuple('ballot', [ 'n', 'leader' ])
