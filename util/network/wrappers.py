# import socket
# import random

from util.console import progress
from util.features import TerminatingInterface
from util.features import Trigger

import pickle
import struct
import errno
import socket


class LocalServer:
    device_interface_ips = []

    def __init__(self, debug_mode=False):
        self.server_ip = None
        self.debug_mode = debug_mode
        # DEBUG_HANDLER
        if not self.debug_mode:
            self._init_interfaces()

    def discover_lan_server(self):
        msg = b'__DISCOVER__'
        print('\r[+] Discovering active servers on LAN')

        progress(4)
        lan_res = self.send_broadcast(msg)
        progress(2)

        # DEBUG_HANDLER
        if self.debug_mode and not lan_res:
            Trigger.SERVER_NOT_FOUND = True
            return

        elif self.debug_mode and lan_res:
            self.server_ip = '127.0.0.1'
            return

        msg = self.receive_broadcast(timeout=2)
        progress(1, re=True)

        if msg is not None:
            self.server_ip = str(msg[1][0])
        else:
            Trigger.SERVER_NOT_FOUND = True

        print('\r[-] Unable to locate LAN Server.' if not msg else '[+] Connecting to an active LAN Server')

    def get_interfaces_len(self):
        return len(self.device_interface_ips)

    def get_server_ip(self):
        return self.server_ip

    def get_singular_interface(self):
        if self.get_interfaces_len() > 1:
            return None
        else:
            return ''.join(self.device_interface_ips)

    def set_server_ip(self, host):
        self.server_ip = host

    def start_lan_server(self) -> None:
        print('\r[+] Activated LAN Server at', self.server_ip)

        while not TerminatingInterface.PROGRAM_TERMINATOR:
            response = self.receive_broadcast(timeout=2)
            if response:
                self.send_broadcast(b'Serving')  # Automatically picks IP from the broadcast, string is only a
                # required argument

    def send_broadcast(self, msg):
        # DEBUG_HANDLE
        if self.debug_mode:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('127.0.0.1', 5005))
                sock.send(msg)
                sock.close()
                return True
            except ConnectionRefusedError:
                return None
        else:
            for ip in self.device_interface_ips:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.bind((ip, 0))
                sock.sendto(msg, ("255.255.255.255", 5005))
                sock.close()

    def receive_broadcast(self, timeout=None):
        # DEBUG_HANDLE
        if self.debug_mode:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('127.0.0.1', 5005))
                sock.settimeout(1)
                sock.listen(2)
                con, addr = sock.accept()
                data = con.recv(1024)
                if data:
                    con.close()
                    return data
            except socket.error:
                pass
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            if timeout:
                sock.settimeout(timeout)
            sock.bind(("0.0.0.0", 5005))
            try:
                data, addr = sock.recvfrom(1024)
                return data, addr
            except socket.timeout:
                pass
            return None

    def _init_interfaces(self):
        interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        self.device_interface_ips = [ip[-1][0] for ip in interfaces]


class SocketWrapper:
    @staticmethod
    def is_socket_valid(socket_instance):
        if not socket_instance:
            return False

        try:
            socket_instance.getsockname()
        except socket.error as err:
            err_type = err.args[0]
            if err_type == errno.EBADF:
                return False

        try:
            socket_instance.getpeername()
        except socket.error as err:
            err_type = err.args[0]
            if err_type in [errno.EBADF, errno.ENOTCONN]:
                return False

        return True

    @staticmethod
    def send_data(conn, data):
        serialized_data = pickle.dumps(data)
        conn.sendall(struct.pack('>I', len(serialized_data)))
        conn.sendall(serialized_data)

    @staticmethod
    def receive_data(conn):
        data_size = struct.unpack('>I', conn.recv(4))[0]
        received_payload = b""
        remaining_payload_size = data_size
        while remaining_payload_size != 0:
            received_payload += conn.recv(remaining_payload_size)
            remaining_payload_size = data_size - len(received_payload)
        data = pickle.loads(received_payload)

        return data

    @staticmethod
    def transaction_listener(sock, ledger, host):
        coms = SocketWrapper()
        sockx = sock
        sockx.settimeout(3)

        while not TerminatingInterface.PROGRAM_TERMINATOR:
            try:
                tx = coms.receive_data(sockx)
                ledger.add_transaction(tx)
                host.update_balance(tx['amount'], 'add')

                print('\r[+] Recorded an incoming transaction of', tx['amount'], 'currency')
                print('\tSender  : ', tx['sender'])
                print('\tReceiver: ', tx['receiver'])
                print('\tHash\t: ', tx['hash'], end='\n> ')

            except struct.error:
                pass
            except socket.timeout:
                pass
            except OSError:
                pass
