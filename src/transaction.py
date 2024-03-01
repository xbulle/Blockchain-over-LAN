import socket
import struct
import random
from hashlib import sha256

from util.network.wrappers import SocketWrapper
from util.features import Nonce, TerminatingInterface


class Transaction:
    listen = True

    def __init__(self, invoker_instance, ledger_instance, dht_instance, target, amount):
        self.host = invoker_instance
        self.ledger = ledger_instance
        self.dht = dht_instance
        self.transaction = self._create(invoker_instance.get_address(),
                                        ledger_instance.get_address_of(target),
                                        amount,
                                        ledger_instance.get_hash())

    @staticmethod
    def _create(sender_address, receiver_address, amount, prev_hash=None):
        lower_bound, upper_bound = Nonce().get_bounds()
        nonce = random.randint(lower_bound, upper_bound)
        if prev_hash:
            local_hash = sha256(str(prev_hash).encode('UTF-8')).hexdigest()
        else:
            local_hash = sha256(str(nonce).encode('UTF-8')).hexdigest()

        return {
            "amount": amount,
            "nonce": nonce,
            "sender": sender_address,
            "receiver": receiver_address,
            "hash": local_hash,
            "previous_hash": None
        }

    def process(self):
        # Get prerequisites ready
        self.host.update_balance(self.transaction['amount'], 'deduct')
        amount = self.transaction['amount']
        sender_address = self.transaction['sender']
        coms = SocketWrapper()

        if self.dht.get_peer_count() > 1:
            individual_mining_share = float((amount * 2) / 100)
            deliverable_amount = amount - float(individual_mining_share * self.dht.get_peer_count())
        else:
            individual_mining_share = 0.0
            deliverable_amount = amount

        # FIXME: Why transact to every participant in the network? (Assuming Mining_Share)
        for i, peer in enumerate(self.dht.get_all_peers()):
            if peer['address'] == sender_address:
                pass

            nodal_socket = self.dht.get_socket(peer['name'])
            amount = deliverable_amount if self.transaction['receiver'] == peer['address'] else individual_mining_share

            coms.send_data(nodal_socket, self.transaction)
            self.ledger.add_transaction(self.transaction)

            print('\r[+] Recorded an outgoing transaction of ' + str(amount), 'currency')
            print('\tSender   :', sender_address)
            print('\tReceiver :', peer['address'], end='\n> ')
