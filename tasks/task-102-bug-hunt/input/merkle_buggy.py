"""
Merkle Tree implementation (BUGGY — contains 5 subtle bugs).
Supports tree construction, proof generation, proof verification, and serialization.
"""
import hashlib
import math


def _hash(data: bytes) -> str:
    """SHA-256 hash, returns hex digest."""
    return hashlib.sha256(data).hexdigest()


def _combine_hashes(left: str, right: str) -> str:
    """Combine two hashes into a parent hash."""
    return _hash((left + right).encode())


class MerkleNode:
    """A node in the Merkle tree."""

    def __init__(self, hash_value: str, left=None, right=None, parent=None):
        self.hash = hash_value
        self.left = left
        self.right = right
        # BUG 5: Storing parent reference creates circular references
        # that prevent garbage collection and break serialization
        self.parent = parent

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


class MerkleTree:
    """A complete Merkle tree."""

    def __init__(self, data_list: list):
        """Build a Merkle tree from a list of data items.

        Args:
            data_list: List of bytes or string items.
        """
        # BUG 3: No handling for empty data list — will crash
        self.leaves = []
        self.root = None
        self._data = data_list
        self._build(data_list)

    def _build(self, data_list: list):
        """Build the tree from data items."""
        # Convert strings to bytes
        items = []
        for item in data_list:
            if isinstance(item, str):
                items.append(item.encode())
            else:
                items.append(item)

        # Create leaf nodes
        self.leaves = [MerkleNode(_hash(item)) for item in items]

        # Build tree bottom-up
        current_level = self.leaves[:]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    # Odd number: duplicate the last node
                    right = current_level[i]

                # BUG 2: Hash concatenation order is wrong — should be left+right
                # but for right children the order matters for proof verification
                parent_hash = _combine_hashes(right.hash, left.hash)
                parent = MerkleNode(parent_hash, left, right)
                # BUG 5 continued: setting parent creates circular ref
                left.parent = parent
                right.parent = parent
                next_level.append(parent)
            current_level = next_level

        self.root = current_level[0]

    @property
    def root_hash(self) -> str:
        """Get the root hash of the tree."""
        return self.root.hash

    @property
    def height(self) -> int:
        """Get the height of the tree."""
        if not self.leaves:
            return 0
        # BUG 1: Off-by-one — should be ceil(log2(n)) + 1 for height,
        # but this returns ceil(log2(n)) which is one less than correct
        return math.ceil(math.log2(len(self.leaves)))

    def get_proof(self, index: int) -> list:
        """Generate a Merkle proof for the leaf at the given index.

        Returns:
            List of (hash, direction) tuples, where direction is 'left' or 'right',
            indicating the sibling hash and which side it's on.
        """
        if index < 0 or index >= len(self.leaves):
            raise IndexError(f"Leaf index {index} out of range [0, {len(self.leaves)})")

        proof = []
        current_level = self.leaves[:]
        current_index = index

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = current_level[i]

                parent_hash = _combine_hashes(right.hash, left.hash)
                next_level.append(MerkleNode(parent_hash))

            # Add sibling to proof
            if current_index % 2 == 0:
                # Current is left child, sibling is right
                if current_index + 1 < len(current_level):
                    proof.append((current_level[current_index + 1].hash, "right"))
                else:
                    # BUG 4: When odd number of nodes, the last node is duplicated
                    # but we don't add anything to proof — verification will fail
                    pass
            else:
                # Current is right child, sibling is left
                proof.append((current_level[current_index - 1].hash, "left"))

            current_index = current_index // 2
            current_level = next_level

        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: list, root_hash: str) -> bool:
        """Verify a Merkle proof.

        Args:
            leaf_hash: Hash of the leaf to verify.
            proof: List of (hash, direction) tuples.
            root_hash: Expected root hash.

        Returns:
            True if the proof is valid.
        """
        current = leaf_hash
        for sibling_hash, direction in proof:
            if direction == "left":
                current = _combine_hashes(sibling_hash, current)
            else:
                current = _combine_hashes(current, sibling_hash)
        return current == root_hash

    def to_dict(self) -> dict:
        """Serialize the tree to a dictionary."""
        def _node_to_dict(node):
            if node is None:
                return None
            return {
                "hash": node.hash,
                "left": _node_to_dict(node.left),
                "right": _node_to_dict(node.right),
            }

        return {
            "root": _node_to_dict(self.root),
            "leaves": [leaf.hash for leaf in self.leaves],
            "data_count": len(self._data),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MerkleTree":
        """Reconstruct a tree from a dictionary (re-builds from data)."""
        # Note: This requires the original data, so it's a simplified version
        # that rebuilds from the stored leaf count
        raise NotImplementedError(
            "from_dict requires original data. Use the constructor instead."
        )
