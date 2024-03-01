from util.proofs.merkle_tree import MerkleTree, hashTable
from hashlib import sha256


def merkle_proof(participant_at_stake, ledger=None) -> bool:
    if consensus():
        ledger.add_participant(participant=participant_at_stake)

    addresses_list = []
    for participant in ledger.get_participants():
        addresses_list.append(participant['address'])

    mtree = MerkleTree(addresses_list)
    mtree.resolve_hash_table()
    mtree.remove_duplications()

    target_hash = sha256(participant_at_stake['address'].encode('UTF-8')).hexdigest()

    if target_hash in hashTable:
        return True
    return False


def consensus() -> bool:
    proficiency = 0.5121564

    if proficiency > 0.5:
        return True

    return False
