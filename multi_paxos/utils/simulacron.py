"""Logger"""
import logging

class SimulacronLogger(logging.LoggerAdapter):
    """Simulated Logger - injects timestamp into all log messages
    """
    def process(self, message, kwargs):
        return 'T=%.4f %s' % (self.extra['network'].now, message), kwargs

    def get_child(self, name):
        return self.__class__(
            self.logger.getChild(name),
            { 'network': self.extra['network'] }
        )
