"""Base Network Protocol"""

import copy
import functools
import heapq
import random

from ..parliament.node import Node

from .timer import Timer

class Network():
    """Simulated Network Protocol - a deterministic simulator
    (behaves exactly the same given the same randomgen seed)

    Simulates packet loss and message propagation delays
    """
    PROP_DELAY = 0.03
    PROP_JITTER = 0.02
    DROP_PROBABILITY = 0.05

    def __init__(self, seed):
        self.nodes = { }
        self.random = random.Random(seed)
        self.timers = []
        self.now = 1000.0

    def new_node(self, addr=None):
        node = Node(self, addr=addr)
        self.nodes[node.addr] = node
        return node

    def run(self):
        while self.timers:
            next_timer = self.timers[0]

            if next_timer.expires > self.now:
                self.now = next_timer.expires

            heapq.heappop(self.timers)

            if next_timer.cancelled:
                continue

            if not next_timer.addr or next_timer.addr in self.nodes:
                next_timer.cb()

    def stop(self):
        self.timers = []

    def set_timer(self, addr, seconds, cb):
        timer = Timer(self.now + seconds, addr, cb)

        heapq.heappush(self.timers, timer)

        return timer

    def send(self, sender, dests, message):
        sender.logger.debug(
            f'Sending {message} to {dests}'
        )

        # avoid aliasing by making discrete copy of message for ea dest
        def send_to(dest, message):
            if dest == sender.addr:
                # send with no delay
                self.set_timer(
                    sender.addr,
                    0,
                    lambda: sender.recv(sender.addr, message)
                )

            # simulate message propagation delay
            elif self.random.uniform(0, 1.0) > self.DROP_PROBABILITY:
                delay = self.PROP_DELAY + self.random.uniform(
                    -self.PROP_JITTER,
                    self.PROP_JITTER
                )

                self.set_timer(
                    dest,
                    delay,
                    functools.partial(
                        self.nodes[dest].recv,
                        sender.addr,
                        message
                    )
                )

        for dest in (d for d in dests if d in self.nodes):
            send_to(dest, copy.deepcopy(message))
