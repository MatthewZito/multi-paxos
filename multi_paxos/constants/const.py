"""Protocol Constants"""

from .message_types import BALLOT, PROPOSAL

JOIN_RETRANSMIT = 0.7
CATCHUP_INTERVAL = 0.6
ACCEPT_RETRANSMIT = 1.0
PREPARE_RETRANSMIT = 1.0
INVOKE_RETRANSMIT = 0.5
LEADER_TIMEOUT = 1.0
NULL_BALLOT = BALLOT(-1, -1)  # sorts before all real ballots
NOOP_PROPOSAL = PROPOSAL(None, None, None)  # noop to fill otherwise empty slots
