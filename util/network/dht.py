import random
import os
import json
import base64

from util.cryptography import DigitalSignature


class DHT:

    def __str__(self) -> str:
        separator = '+-------+' + '-'*32 + '+\n'

        format_dht = separator
        format_dht += '|  name |\t\t\t\t\t\taddress  |\n'
        format_dht += separator

        for node in self.dht:
            format_dht += '| {}\t| {} |\n'.format(node['name'], node['address'])

        format_dht += separator
        return format_dht

    def __init__(self):
        self.dht = []

    def add_peer(self, name, address, sock):
        peer = {
            'name': name,
            'address': address,
            'socket_id': len(self.dht) + 1,
            'socket': sock
        }
        self.dht.append(peer)

    def close_all_sockets(self):
        self.dht.clear()

    def close_socket(self, name):
        for i, node in enumerate(self.dht):
            if name == node['name']:
                self.dht.pop(i)['socket'].close()

    def get_socket(self, name):
        for node in self.dht:
            if name == node['name']:
                return node['socket']

    def get_packed_dht(self):
        return self.dht

    def get_peer_count(self):
        return len(self.dht)

    def get_targeted_peer(self, target):
        for node in self.dht:
            if target == node['name']:
                return node

    def connection_status(self, target):
        if self.get_targeted_peer(target):
            return True
        return False

    def get_all_peers(self):
        return self.dht


class Host:
    def __init__(self, debug_mode=False):
        cur = os.path.abspath(os.path.curdir)
        self.path = cur + '\\locale\\host.json'
        self.debug_mode = debug_mode
        self.secret, self.public = None, None

        if not debug_mode:
            self.host = self.read_host()
        else:
            self.host = self.generate_host()

        # print(type(self.public))

    def generate_host(self):
        self.secret, self.public = DigitalSignature.generate_signature()
        return {
            'name': self.get_new_addr()[10:14],
            'address': self.get_new_addr(),
            'nonce': random.randint(1892, 9999),
            'signatures': [
                {
                    'secret': self.secret,
                    'public': self.public
                }
            ],
            'balance': 99.99
        }

    def get_address(self):
        return self.host['address']

    def get_deliverables(self):
        return {
            'name': self.host['name'],
            'address': self.host['address'],
            'signature': self.public
        }

    @staticmethod
    def get_new_addr():
        return str('%030x' % random.randrange(16 ** 30))

    def get_name(self):
        return self.host['name']

    def get_balance(self):
        return float(self.host['balance'])

    def update_balance(self, balance, action: str):
        if action == 'deduct':
            self.host['balance'] -= balance
        elif action == 'add':
            self.host['balance'] += balance
        # DEBUG_HANDLE
        if not self.debug_mode:
            self.save_host_as_json()

    def read_host(self):
        if not os.path.exists(self.path):
            f = open(self.path, "w")
            f.close()

        with open(self.path, 'r+') as file:
            try:
                data = json.load(file)

                self.public = base64.b64decode(data['signatures'][0]['public'].encode('utf-8'))
                self.secret = base64.b64decode(data['signatures'][0]['secret'].encode('utf-8'))

            except json.decoder.JSONDecodeError:
                self.secret, self.public = DigitalSignature.generate_signature()
                data = {
                    'name': self.get_new_addr()[10:14],
                    'address': self.get_new_addr(),
                    'nonce': random.randint(1892, 9999),
                    'role': 'standard',
                    'signatures': [
                        {
                            'secret': base64.b64encode(self.secret).decode('UTF-8'),
                            'public': base64.b64encode(self.public).decode('UTF-8')
                        }
                    ],
                    'balance': 99.99
                }
                json.dump(data, file, indent=2)
        return data

    def save_host_as_json(self):
        with open(self.path, 'w+') as file:
            file.truncate(0)
            json.dump(self.host, file)
            file.close()

    def update_name(self, name):
        self.host['name'] = name
        # DEBUG_HANDLE
        if not self.debug_mode:
            self.save_host_as_json()
