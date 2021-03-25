import logging
import sys

from .network.network import Network
from .roles.initializer import Initializer
from .roles.requester import Requester
from .roles.seed import Seed

from .utils.printer import Colors

from .state_machines.key_value_machine import state_machine

seq_active = 0

def proc_sequence(network, node, key):
    global seq_active

    seq_active += 1

    mock_requests = [
        (('get', key), None),
        (('set', key, 9), 9),
        (('get', key), 9),
        (('set', key, 6), 6),
        (('set', key, 32), 32),
        (('get', key), 32),
        (('set', key, 39), 39),
        (('get', key), 39),
        (('set', key, 66), 66),
        (('set', key, 77), 77),
        (('get', key), 77)
    ]

    # mock_requests = [
    #     (('balance', key), 0),
    #     (('deposit', key, 9), 9),
    #     (('balance', key), 9),
    #     (('withdraw', key, 6), 6),
    # ]

    def request():
        if not mock_requests:
            global seq_active
            seq_active -= 1

            if not seq_active:
                network.stop()
            return

        inp, out = mock_requests.pop(0)

        def done(output):
            assert output == out, f'{output} != {out}'
            request()

        Requester(
            node,
            inp,
            done
        ).start()

    network.set_timer(
        None,
        1.0,
        request
    )


def main():
    pointer = '--->'
    logging.basicConfig(
        format=f'{Colors.BOLD}{Colors.OKGREEN}%(name)s{Colors.ENDC}{Colors.FAIL} {pointer} {Colors.ENDC} %(message)s{Colors.ENDC}',
        level=logging.DEBUG
    )

    network = Network(int(sys.argv[1]))

    peers = ['NODE_%d' % i for i in range(14)]

    for peer in peers:
        node = network.new_node(addr=peer)

        if peer == 'NODE_0':
            Seed(
                node,
                initial_state={},
                peers=peers,
                executor=state_machine
            )

        else:
            Initializer(
                node,
                executor=state_machine,
                peers=peers
            ).start()

    for key in 'ABCD':
        proc_sequence(
            network,
            node,
            key
        )

    network.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n[!] Execution stopped by user')
