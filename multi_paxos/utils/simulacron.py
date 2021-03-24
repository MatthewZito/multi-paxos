import logging

"""TODO"""
class SimulacronLogger(logging.LoggerAdapter):
    """[summary]

    Args:
        logging ([type]): [description]
    """

    def process(self, message, kwargs):
        return 'T=%.4f %s' % (self.extra['network'].now, message), kwargs

    def get_child(self, name):
        return self.__class__(
            self.logger.get_child(name),
            { 'network': self.extra['network'] }
        )
