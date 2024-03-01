import json
import random
import os
from hashlib import sha256

from util.features import Nonce
from util.features import Trigger


class Ledger:
    def __init__(self, host, nonce_limit=4, debug_mode=False):
        # Objects to utilities
        self.host = host
        self.nonce = Nonce(nonce_limit=nonce_limit)

        self.debug_mode = debug_mode
        self.transactions_per_block = 20
        self.ledger = {}
        self.current_transaction_hash = ''
        self.current_block = 0
        cur = os.path.abspath(os.path.curdir)
        self.path = cur + '\\locale\\ledger.json'

        self._refresh_ledger()

    def add_block(self, list_of_transactions, miner_address):
        local_hash = sha256(self.current_transaction_hash)

        new_block = {
            "block_number": self.current_block + 1,
            "transactions": list_of_transactions,
            "miner": miner_address
        }

        new_block.update({'block_hash': sha256(str(new_block).encode('UTF-8')).hexdigest()})

        self.current_transaction_hash = local_hash
        self.current_block += 1

        self.ledger['blocks'][self.current_block]['transactions'].append(new_block)
        if not self.debug_mode:
            self._save_ledger()
        return new_block

    def add_participant(self, name=None, address=None, participant=None):
        if participant:
            if participant not in self.ledger['participants']:
                self.ledger['participants'].append(participant)
        elif name and address:
            if name not in self.ledger['participants']:
                self.ledger['participants'].append(self.make_participant_from_data(name, address))
        else:
            raise 'Invalid arguments supplied for add_participants()'

    def add_transaction(self, transaction):
        self.ledger['blocks'][self.current_block]['transactions'].append(transaction)
        self.ledger['blocks'][self.current_block].update(
            {'block_hash': sha256(str(self.ledger['blocks'][self.current_block]).encode('UTF-8')).hexdigest()}
        )
        if not self.debug_mode:
            self._save_ledger()

    def _block_space_measurement(self):
        return True if len(self.ledger['blocks'][-1]) < self.transactions_per_block else False

    def _create_genesis_block(self):
        block_number = 0
        nonce = random.randint(self.nonce.lower_bound, self.nonce.upper_bound)
        local_hash = sha256(str(nonce).encode('UTF-8')).hexdigest()

        genesis_block = {
            "block_number": 0,
            "transactions": [
                {
                    "amount": 99.99,
                    "nonce": nonce,
                    "sender": None,
                    "receiver": self.host.get_address(),
                    "hash": local_hash,
                    "previous_hash": None
                }
            ],
            "miner": None
        }
        genesis_block.update(
            {'block_hash': sha256(str(genesis_block).encode('UTF-8')).hexdigest()}
        )

        self.ledger = {
            "participants": [
                self.make_participant_from_data(self.host.get_name(), self.host.get_address())
            ],
            "blocks": [
                genesis_block
            ]
        }

        self.current_transaction_hash = local_hash
        self.current_block = block_number

    def get_address_of(self, target_name):
        return ''.join([p['address'] for p in self.ledger['participants'] if p['name'] == target_name])

    def get_hash(self):
        return self.current_transaction_hash

    def get_value(self, key, nest=None):
        if nest:
            return self.ledger[str(key)][str(nest)]
        else:
            return self.ledger[str(key)]

    def get_participants(self):
        return self.ledger['participants']

    def make_participant_from_data(self, name, address):
        new_participant = {
            "name": name,
            "address": address,
            "account_type": "standard",
            "hash": self.participant_hash(name, address)
        }
        return new_participant

    def _refresh_ledger(self):
        # DEBUG_HANDLE
        if self.debug_mode:
            self._create_genesis_block()
            return

        with open(self.path, 'r+') as file:
            try:
                self.ledger = json.load(file)
                self.current_block = self.ledger['blocks'][-1]['block_number']

                # Hash of the latest transaction
                self.current_transaction_hash = self.ledger['blocks'][-1]['transactions'][-1]['hash']

            except json.decoder.JSONDecodeError:  # Ledger is unreadable or doesn't exist
                self._create_genesis_block()
                self._save_ledger()

    def participant_hash(self, host_name=None, host_address=None):
        part_dict = {
            "name": host_name,
            "address": host_address
        }
        part_hash = sha256(str(part_dict).encode('UTF-8')).hexdigest()
        part_dict.update({'hash': part_hash})

        # Hash the dictionary including base hash
        return sha256(str(part_dict).encode('UTF-8')).hexdigest()

    def _save_ledger(self):
        with open(self.path, 'r+') as file:
            file.truncate(0)
            json.dump(self.ledger, file, indent=2)

    def update_name(self, name, target):
        target_id = -1

        for i, x in enumerate(self.ledger['participants']):
            if x['name'] == target:
                target_id = i
                break

        if target_id < 0:
            raise 'Target not found.'

        self.ledger['participants'][target_id]['name'] = name

        # DEBUG_HANDLE
        if not self.debug_mode:
            self._save_ledger()
