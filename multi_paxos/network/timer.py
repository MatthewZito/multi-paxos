"""Base Timer"""

from functools import total_ordering

@total_ordering
class Timer():
    """Timer simulation - Schedules delayed message delivery for protocol simulation

    Pops timers off of heapq for selection of next event
    Each timer uses a random, simulated delay for scheduling message delivery at each Node

    Given removing items from a heap is inefficient, cancelled timers are left in place
    but marked `cancelled`

    Timers are executed if and only if they have not been cancelled AND the destination Node
    is still in an active state
    """

    def __init__(self, expires, addr, cb):
        self.expires = expires
        self.addr = addr
        self.cb = cb
        self.cancelled = False

    def __eq__(self, other):
        return self.expires == other.expires

    def __ne__(self, other):
        return not self.expires == other.expires

    def __lt__(self, other):
        return self.expires < other.expires

    def cancel(self):
        self.cancelled = True
