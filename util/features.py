class Nonce:
    lower_bound = 0
    upper_bound = 0

    def __init__(self, nonce_limit=4):
        self.lower_bound = int(''.join(['1' for _ in range(0, nonce_limit)]))
        self.upper_bound = int(''.join(['9' for _ in range(0, nonce_limit)]))

    def get_bounds(self):
        return self.lower_bound, self.upper_bound

    def recalculate(self, nonce_limit):
        self.lower_bound = int(''.join(['1' for _ in range(0, nonce_limit)]))
        self.upper_bound = int(''.join(['9' for _ in range(0, nonce_limit)]))


class TerminatingInterface:
    PROGRAM_TERMINATOR = False


class Trigger:
    DEBUG_MODE = False
    SERVER_NOT_FOUND = False
    RUNNING_AS_SERVER = False

