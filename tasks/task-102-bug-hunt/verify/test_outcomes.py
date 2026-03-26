"""Outcome-based tests for task-102: Bug hunt — fix the Merkle tree."""
import gc
import hashlib
import importlib.util
import os
import sys
import weakref
import pytest

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())


def _load_merkle():
    path = os.path.join(OUTPUT_DIR, "merkle.py")
    if not os.path.exists(path):
        pytest.skip(f"merkle.py not found in {OUTPUT_DIR}")
    spec = importlib.util.spec_from_file_location("merkle", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def M():
    return _load_merkle()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _combine(left: str, right: str) -> str:
    return hashlib.sha256((left + right).encode()).hexdigest()


# ===========================================================================
# SECTION 1: Basic hashing (3 tests)
# ===========================================================================

def test_single_leaf_hash(M):
    tree = M.MerkleTree([b"hello"])
    expected = _sha256(b"hello")
    assert tree.root_hash == expected


def test_two_leaves_hash(M):
    h0 = _sha256(b"aaa")
    h1 = _sha256(b"bbb")
    expected_root = _combine(h0, h1)
    tree = M.MerkleTree([b"aaa", b"bbb"])
    assert tree.root_hash == expected_root


def test_string_input(M):
    tree = M.MerkleTree(["hello"])
    expected = _sha256(b"hello")
    assert tree.root_hash == expected


# ===========================================================================
# SECTION 2: Empty tree — BUG 3 (3 tests)
# ===========================================================================

def test_empty_tree_no_crash(M):
    """Empty data must not crash."""
    tree = M.MerkleTree([])
    assert tree.root_hash is not None or tree.root is None


def test_empty_tree_root_is_none_or_empty_hash(M):
    tree = M.MerkleTree([])
    # Either root is None, or root_hash is a well-defined empty hash
    if tree.root is None:
        assert True
    else:
        assert isinstance(tree.root_hash, str) and len(tree.root_hash) == 64


def test_empty_tree_height(M):
    tree = M.MerkleTree([])
    assert tree.height == 0


# ===========================================================================
# SECTION 3: Tree height — BUG 1 (5 tests)
# ===========================================================================

def test_height_single(M):
    tree = M.MerkleTree([b"x"])
    # Single leaf: height is 1 (just the root which is the leaf)
    assert tree.height == 1


def test_height_two(M):
    tree = M.MerkleTree([b"a", b"b"])
    assert tree.height == 2


def test_height_three(M):
    tree = M.MerkleTree([b"a", b"b", b"c"])
    assert tree.height == 3


def test_height_four(M):
    tree = M.MerkleTree([b"a", b"b", b"c", b"d"])
    assert tree.height == 3


def test_height_eight(M):
    tree = M.MerkleTree([bytes([i]) for i in range(8)])
    assert tree.height == 4


# ===========================================================================
# SECTION 4: Hash concatenation order — BUG 2 (4 tests)
# ===========================================================================

def test_four_leaves_root(M):
    items = [b"a", b"b", b"c", b"d"]
    h = [_sha256(x) for x in items]
    left_parent = _combine(h[0], h[1])
    right_parent = _combine(h[2], h[3])
    expected_root = _combine(left_parent, right_parent)
    tree = M.MerkleTree(items)
    assert tree.root_hash == expected_root


def test_hash_order_matters(M):
    """Tree([a,b]) != Tree([b,a])."""
    t1 = M.MerkleTree([b"x", b"y"])
    t2 = M.MerkleTree([b"y", b"x"])
    assert t1.root_hash != t2.root_hash


def test_three_leaves_root(M):
    items = [b"a", b"b", b"c"]
    h = [_sha256(x) for x in items]
    left_parent = _combine(h[0], h[1])
    # Odd: last node is duplicated
    right_parent = _combine(h[2], h[2])
    expected_root = _combine(left_parent, right_parent)
    tree = M.MerkleTree(items)
    assert tree.root_hash == expected_root


def test_deterministic(M):
    data = [b"one", b"two", b"three"]
    t1 = M.MerkleTree(data)
    t2 = M.MerkleTree(data)
    assert t1.root_hash == t2.root_hash


# ===========================================================================
# SECTION 5: Proof generation & verification (8 tests)
# ===========================================================================

def test_proof_single_item(M):
    tree = M.MerkleTree([b"only"])
    proof = tree.get_proof(0)
    assert M.MerkleTree.verify_proof(_sha256(b"only"), proof, tree.root_hash)


def test_proof_two_items_left(M):
    tree = M.MerkleTree([b"a", b"b"])
    proof = tree.get_proof(0)
    assert M.MerkleTree.verify_proof(_sha256(b"a"), proof, tree.root_hash)


def test_proof_two_items_right(M):
    tree = M.MerkleTree([b"a", b"b"])
    proof = tree.get_proof(1)
    assert M.MerkleTree.verify_proof(_sha256(b"b"), proof, tree.root_hash)


def test_proof_four_items_all(M):
    items = [b"w", b"x", b"y", b"z"]
    tree = M.MerkleTree(items)
    for i, item in enumerate(items):
        proof = tree.get_proof(i)
        assert M.MerkleTree.verify_proof(
            _sha256(item), proof, tree.root_hash
        ), f"Proof failed for index {i}"


def test_proof_three_items_last(M):
    """Odd-length level — BUG 4 area."""
    items = [b"a", b"b", b"c"]
    tree = M.MerkleTree(items)
    proof = tree.get_proof(2)
    assert M.MerkleTree.verify_proof(_sha256(b"c"), proof, tree.root_hash)


def test_proof_five_items(M):
    items = [bytes([i]) for i in range(5)]
    tree = M.MerkleTree(items)
    for i in range(5):
        proof = tree.get_proof(i)
        assert M.MerkleTree.verify_proof(
            _sha256(items[i]), proof, tree.root_hash
        ), f"Proof failed for index {i}"


def test_proof_seven_items(M):
    items = [f"item{i}".encode() for i in range(7)]
    tree = M.MerkleTree(items)
    for i in range(7):
        proof = tree.get_proof(i)
        assert M.MerkleTree.verify_proof(
            _sha256(items[i]), proof, tree.root_hash
        ), f"Proof failed for index {i}"


def test_invalid_proof_rejected(M):
    tree = M.MerkleTree([b"a", b"b", b"c", b"d"])
    proof = tree.get_proof(0)
    # Tamper with the proof
    tampered = [(h + "0", d) if idx == 0 else (h, d) for idx, (h, d) in enumerate(proof)]
    assert not M.MerkleTree.verify_proof(_sha256(b"a"), tampered, tree.root_hash)


def test_wrong_leaf_rejected(M):
    tree = M.MerkleTree([b"a", b"b"])
    proof = tree.get_proof(0)
    assert not M.MerkleTree.verify_proof(_sha256(b"WRONG"), proof, tree.root_hash)


def test_proof_index_out_of_range(M):
    tree = M.MerkleTree([b"a", b"b"])
    with pytest.raises((IndexError, ValueError)):
        tree.get_proof(5)


# ===========================================================================
# SECTION 6: Large tree (3 tests)
# ===========================================================================

def test_large_tree_1000(M):
    items = [f"data_{i}".encode() for i in range(1000)]
    tree = M.MerkleTree(items)
    assert isinstance(tree.root_hash, str) and len(tree.root_hash) == 64


def test_large_tree_proof_verification(M):
    items = [f"d{i}".encode() for i in range(1000)]
    tree = M.MerkleTree(items)
    # Verify random indices
    for i in [0, 1, 499, 500, 998, 999]:
        proof = tree.get_proof(i)
        assert M.MerkleTree.verify_proof(_sha256(items[i]), proof, tree.root_hash)


def test_power_of_two_tree(M):
    items = [bytes([i % 256]) for i in range(256)]
    tree = M.MerkleTree(items)
    proof = tree.get_proof(128)
    assert M.MerkleTree.verify_proof(_sha256(items[128]), proof, tree.root_hash)


# ===========================================================================
# SECTION 7: Serialization (3 tests)
# ===========================================================================

def test_to_dict(M):
    tree = M.MerkleTree([b"a", b"b", b"c"])
    d = tree.to_dict()
    assert "root" in d
    assert "leaves" in d
    assert len(d["leaves"]) == 3


def test_to_dict_hashes_correct(M):
    tree = M.MerkleTree([b"hello", b"world"])
    d = tree.to_dict()
    assert d["leaves"][0] == _sha256(b"hello")
    assert d["leaves"][1] == _sha256(b"world")


def test_serialization_no_crash(M):
    """Serialization must not crash due to circular references (BUG 5)."""
    import json
    tree = M.MerkleTree([b"a", b"b", b"c", b"d"])
    d = tree.to_dict()
    # Must be JSON-serializable (no circular refs)
    json_str = json.dumps(d)
    assert len(json_str) > 0


# ===========================================================================
# SECTION 8: No circular references — BUG 5 (3 tests)
# ===========================================================================

def test_no_parent_attribute(M):
    """Nodes should not have a parent reference (causes circular refs)."""
    tree = M.MerkleTree([b"a", b"b"])
    # Check that parent is either absent or None
    root = tree.root
    parent_val = getattr(root, "parent", None)
    assert parent_val is None, "Root node should not have a parent reference to avoid circular refs"


def test_gc_collectable(M):
    """Tree should be garbage-collectible (no reference cycles blocking GC)."""
    tree = M.MerkleTree([b"x", b"y", b"z"])
    root_ref = weakref.ref(tree)
    del tree
    gc.collect()
    # After deletion and GC, the weakref should be dead
    assert root_ref() is None, "Tree was not garbage collected — likely circular refs"


def test_leaf_no_circular_ref(M):
    """Leaf nodes should not reference parents."""
    tree = M.MerkleTree([b"a", b"b", b"c", b"d"])
    for leaf in tree.leaves:
        parent_val = getattr(leaf, "parent", None)
        assert parent_val is None, "Leaf nodes should not hold parent references"
