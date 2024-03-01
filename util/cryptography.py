from typing import Any

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class DigitalSignature:

    @staticmethod
    def generate_signature():
        key_pair = RSA.generate(1024)

        public_key = key_pair.publickey().exportKey('DER')
        private_key = key_pair.exportKey('DER')

        return private_key, public_key

        # key = RSA.importKey(public_key)
        # message = b'A message to secure'
        # print(message, "< ======== To secure")
        #
        # cipher = PKCS1_OAEP.new(key)
        # ciphertext = cipher.encrypt(message)
        # print("Encryption", ciphertext)
        #
        # key = RSA.importKey(private_key)
        # cipher = PKCS1_OAEP.new(key)
        # decrypted_message = cipher.decrypt(ciphertext)
        # print("Decrypted", decrypted_message)


DigitalSignature.generate_signature()
