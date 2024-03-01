from typing import List
import hashlib

hashTable = []


class Node:
    def __init__(self, left, right, value: str, content, is_copied=False) -> None:
        self.left: Node = left
        self.right: Node = right
        self.value = value
        self.content = content
        self.is_copied = is_copied

    @staticmethod
    def hash(val: str) -> str:
        return hashlib.sha256(val.encode('utf-8')).hexdigest()

    def __str__(self):
        return (str(self.value))

    def copy(self):
        """
        class copy function
        """
        return Node(self.left, self.right, self.value, self.content, True)


class MerkleTree:
    def __init__(self, values: List[str]) -> None:
        self.__build_tree(values)

    def __build_tree(self, values: List[str]) -> None:
        leaves: List[Node] = [Node(None, None, Node.hash(e), e) for e in values]
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1].copy())  # duplicate last elem if odd number of elements
        self.root: Node = self.__build_tree_rec(leaves)

    def __build_tree_rec(self, nodes: List[Node]) -> Node:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1].copy())  # duplicate last elem if odd number of elements
        half: int = len(nodes) // 2

        if len(nodes) == 2:
            return Node(nodes[0], nodes[1], Node.hash(nodes[0].value + nodes[1].value), nodes[0].content+"+"+nodes[1].content)

        left: Node = self.__build_tree_rec(nodes[:half])
        right: Node = self.__build_tree_rec(nodes[half:])
        value: str = Node.hash(left.value + right.value)
        content: str = f'{left.content}+{right.content}'
        return Node(left, right, value, content)

    def resolve_hash_table(self) -> None:
        self.__recursive_resolver(self.root, suppressed=True)

    def __recursive_resolver(self, node: Node, suppressed=False) -> None:
        if node is not None:
            hashTable.append(node.value)
            self.__recursive_resolver(node.left)
            self.__recursive_resolver(node.right)

    def get_root_hash(self) -> str:
        return self.root.value

    @staticmethod
    def remove_duplications():
        global hashTable

        temp_hash_table = []
        [temp_hash_table.append(x) for x in hashTable if x not in temp_hash_table]
        # for hash in hashTable:
        #     if hash not in temp:
        #         temp.append(i)
        hashTable = temp_hash_table


# def mixmerkletree() -> None:
#     elems = ["Mix", "Merkle", "Tree", "From", "Onur Atakan ULUSOY", "https://github.com/onuratakan/mixmerkletree", "GO"]
#     print("Inputs: ")
#     print(*elems, sep=" | ")
#     print("")
#     mtree = MerkleTree(elems)
#     print("Root Hash: " + mtree.get_root_hash() + "\n")
#     mtree.resolve_hash_table()
#     print(len(hashTable))
#     print(len(elems))
#     # hashTable = set(hashTable)
#
#
# mixmerkletree()
#
# temp = []
# for i in hashTable:
#     # print(i)
#     if i not in temp:
#         temp.append(i)
#
# print(len(temp))
#
# hashTable = temp
# some_val = "Mixe"
# hash_some_val = hashlib.sha256(some_val.encode('utf-8')).hexdigest()
# print("Value found in Table: ", hash_some_val in hashTable)
#
# some_val = "Mix"
# hash_some_val = hashlib.sha256(some_val.encode('utf-8')).hexdigest()
# print("Value found in Table: ", hash_some_val in hashTable)
