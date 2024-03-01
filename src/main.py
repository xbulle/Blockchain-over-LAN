import socket
import threading
import time

from util.features import TerminatingInterface
from util.features import Trigger
from util.console import *
from util.network.dht import *
from proofs import merkle_proof

from util.network.wrappers import LocalServer, SocketWrapper
from ledger import Ledger
from transaction import Transaction

"""
    TODO: #ISSUES
    + Implement Wallet Status
"""
"""
    SUPPLY --enable-debug command line argument in order to use localhost and run on multiple nodes on same PC
"""


def perspectives(*args, **kwargs):
    def client():
        print('\r[+] Requesting to join the blockchain network', end='\n> ')
        print(f'\r[+] Requesting to validate Merkle Proof', end='\n> ')

    def server(local_name) -> None:
        print(f'\r[+] {local_name} requests to join.', end='\n> ')
        print(f'\r[+] Collecting Merkle Proof for {local_name}.', end='\n> ')


def _network_controller(client_sock, ledger, dht, current_host, trigger=None) -> None:
    coms = SocketWrapper()

    coms.send_data(client_sock, current_host.get_deliverables())
    data = coms.receive_data(client_sock)

    participant = ledger.make_participant_from_data(data['name'], data['address'])

    if 'server' in str(trigger).lower():
        print(f'\r[+] {participant["name"]} requests to join.', end='\n> ')
        print(f'\r[+] Collecting Merkle Proof for {participant["name"]}.', end='\n> ')

    if 'client' in str(trigger).lower():
        print('\r[+] Requesting to join the blockchain network', end='\n> ')
        print(f'\r[+] Requesting to validate Merkle Proof', end='\n> ')

    if merkle_proof(participant, ledger=ledger):
        dht.add_peer(data['name'], data['address'], client_sock)

        # TODO: SHARE DHT and LEDGER with new participant

        if 'server' in str(trigger).lower():
            print(f'\r[+] {participant["name"]} has joined the network. `peers` to list connected peers.', end='\n> ')
        else:
            print(f'\r[+] Membership proved; joined the blockchain network. `peers` to list connected peers.', end='\n> ')

        r = threading.Thread(target=coms.transaction_listener, args=(client_sock, ledger, current_host))
        r.daemon = True
        r.start()

        while not TerminatingInterface.PROGRAM_TERMINATOR:
            time.sleep(2)
            if not coms.is_socket_valid(client_sock):
                print(f'\r[-] Participant {participant["name"]} abruptly exited the blockchain network.', end='\n> ')
                break

        dht.close_socket(participant['name'])
        client_sock.close()
    else:
        print('\r[-] MERKLE_PROOF_FAILURE: Participant', participant['name'], 'could not prove membership.\n> ')
        client_sock.close()


def connection_listener(sock, ledger, dht, host) -> None:
    while not TerminatingInterface.PROGRAM_TERMINATOR:
        try:
            client, address = sock.accept()

            c = threading.Thread(target=_network_controller, args=(client, ledger, dht, host, 'server'))
            c.daemon = True
            c.start()

        except TimeoutError:
            pass


if __name__ == '__main__':
    debug_mode = resolve_program_mode()  # Reads cli arguments

    # Initialize Required Objects
    dht = DHT()
    endpoint = LocalServer(debug_mode=debug_mode)
    invoker = Host(debug_mode=debug_mode)
    ledger = Ledger(host=invoker, nonce_limit=8, debug_mode=debug_mode)

    active_threads = []
    host, PORT = -1, 28545
    sock = socket.socket()
    sock.settimeout(3)  # FIXME: Reduce wait time to immediately accept connections

    """
        LocalServer.discover_lan_server() -> None
            - Uses globally declared triggers : util.features.Trigger
            - Sets the global trigger "SERVER_NOT_FOUND" that can be used anywhere in the code.
        : doesn't manipulate anything else
    """
    endpoint.discover_lan_server()

    if Trigger.SERVER_NOT_FOUND:
        # DEBUG_HANDLE
        if not debug_mode:
            if endpoint.get_interfaces_len() > 1:

                print('\r[*] Multiple interfaces found; select an interface to activate server on')
                for i, interface in enumerate(endpoint.device_interface_ips):
                    print('\tInt' + str(i), ':', interface)
                print("HINT: Int0 for interface 0")

                host = str(endpoint.device_interface_ips[int("".join([char for char in input('> ') if char.isdigit()]))])

            else:
                host = str(endpoint.get_singular_interface())
        else:
            host = '127.0.0.1'

        endpoint.set_server_ip(host)

        server = threading.Thread(target=endpoint.start_lan_server, name='LAN Server')
        active_threads.append(server)
        server.start()

        try:
            sock.bind((host, PORT))
        except socket.error as e:
            print(str(e))

        sock.listen(5)

        listener = threading.Thread(target=connection_listener, args=(sock, ledger, dht, invoker), name='Client Helper')
        active_threads.append(listener)
        listener.start()

    else:
        try:
            sock.connect((endpoint.get_server_ip(), PORT))
        except socket.error as e:
            print(str(e))

        # _network_controller.perspective = perspectives

        client_end = threading.Thread(target=_network_controller, args=(sock, ledger, dht, invoker, 'client'), name='Client')
        active_threads.append(client_end)
        client_end.start()

    print_usage_prompt()

    while not TerminatingInterface.PROGRAM_TERMINATOR:
        try:
            cmd = input('\r> ')
            if 'tx' in cmd or 'transact' in cmd and not len(cmd.split()) > 3:
                given = {'amount': float(cmd.split()[1]), 'target': str(cmd.split()[2])}

                if dht.get_peer_count():    # Has at least one peer connected

                    if dht.connection_status(given['target']) and float(invoker.get_balance() - given['amount']) >= 0:
                        transaction = Transaction(invoker, ledger, dht, given['target'], given['amount'])
                        transaction.process()
                        del transaction
                    else:
                        print('Unable to locate participant or amount exceeded wallet balance.')

                else:
                    print('[+] No peers connected. Please run `python main.py` on another device in same LAN.')

            elif 'peers' in cmd:
                print(str(dht) if dht.get_peer_count() else '[+] No peers connected. Please run `python main.py` on'
                                                            'another device in same LAN.')

            elif 'status' in cmd:
                # TODO: print_wallet_status()
                pass

            elif 'name' in cmd:
                try:
                    name = cmd.split()[1]
                    ledger.update_name(name, invoker.get_name())
                    invoker.update_name(name)
                    print('\r[+] Peer name changed to', name)
                except IndexError:
                    print('\r[+] Peer name =>', invoker.get_name())

            elif 'close' or 'exit' in cmd:
                TerminatingInterface.PROGRAM_TERMINATOR = True

            else:
                print_usage_prompt()

        except KeyboardInterrupt:
            TerminatingInterface.PROGRAM_TERMINATOR = True

    for t in active_threads:
        print('\r[*] Terminating', t.name)
        t.join()

    sock.close()
