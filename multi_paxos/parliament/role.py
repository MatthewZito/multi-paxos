"""Base Role class"""

class Role():
    """Dynamic construct representing the state of roles for a given cluster node.

    Roles are adjusted throughout the lifetime of the node that has inherited them.
    Messages that arrive on the node are relayed to all active roles.
    """
    def __init__(self, node):
        self.node = node
        self.node.register(self)
        self.running = True
        self.logger = node.logger.get_child(type(self).__name__)

    def set_timer(self, seconds, cb):
        """Invoke node network's set_timer

        Args:
            seconds (int)
            cb (function)

        Returns:
            Timer: reference to timer instance which has been pushed onto the heapq stack
        """
        return self.node.network.set_timer(
            self.node.addr,
            seconds,
            lambda: self.running and cb()
        )

    def stop(self):
        """Deallocate the role from a given node
        """
        self.running = False
        self.node.unregister(self)
