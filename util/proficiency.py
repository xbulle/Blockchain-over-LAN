import random
import time
from hashlib import sha256
from console import progress


def brute_force(hash_to_solve, lower_bound, upper_bound):
    for guessed_nonce in range(lower_bound, upper_bound):
        if sha256(str(guessed_nonce).encode('UTF-8')).hexdigest() == hash_to_solve:
            return


def mean_solving_efficiency(lower_bound, upper_bound, testing_range):
    compute_times = []
    print('Testing Efficiency')
    for i in range(0, testing_range):
        re = True if i == testing_range-1 else False
        progress(int(testing_range-i), re=re)
        random_nonce = random.randint(lower_bound, upper_bound)
        nonce_hashed = sha256(str(random_nonce).encode('UTF-8')).hexdigest()
        tbegin = time.time()*1000
        brute_force(nonce_hashed, lower_bound, upper_bound)
        compute_times.append((time.time()*1000)-tbegin)

    # print(max(compute_times))
    # print(compute_times)
    if 0 in compute_times:
        compute_times.remove(0)
    norm = [float(i)/max(compute_times) for i in compute_times]
    # print(norm)
    print('Participant Efficiency', round(sum(norm)/len(norm), 4))


mean_solving_efficiency(111111, 999999, 20)
