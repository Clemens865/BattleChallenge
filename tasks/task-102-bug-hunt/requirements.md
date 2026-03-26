# Task 102: Bug Hunt — Fix the Merkle Tree

## Objective

You are given a buggy Merkle tree implementation (`input/merkle_buggy.py`). It contains exactly **5 subtle bugs**. Find and fix ALL of them. Output the corrected version as `merkle.py`.

## Input

`input/merkle_buggy.py` — a ~150-line Merkle tree implementation with 5 planted bugs.

## The Implementation Should Support

1. **Construction**: Build a Merkle tree from a list of data items (bytes or strings)
2. **Root hash**: Compute the Merkle root hash
3. **Proof generation**: Generate an inclusion proof for any leaf
4. **Proof verification**: Verify a proof against a root hash (static method)
5. **Serialization**: Convert tree to dict and reconstruct from dict

## Known Bug Descriptions (hints)

You don't know exactly where they are, but the 5 bugs relate to:

1. **Tree height calculation** — off-by-one error
2. **Hash concatenation order** — left/right children swapped in certain cases
3. **Empty data handling** — crashes or returns wrong result for empty input
4. **Odd-length level handling** — proof verification fails when a tree level has odd number of nodes
5. **Circular references** — nodes hold parent references that prevent garbage collection and break serialization

## Required Output

- `merkle.py` — the fixed implementation

## Constraints

- Must use SHA-256 for hashing
- Must handle arbitrary data sizes (empty, single item, powers of 2, non-powers of 2, 1000+ items)
- Proof format: list of (hash, direction) tuples where direction is "left" or "right"
- No external dependencies — only Python standard library
- The fixed version must pass ALL provided tests

## Scoring

**Binary**: ALL tests must pass or score is 0. This is a **two-pass** task — the test suite is run twice and must pass both times (to catch non-deterministic fixes).

Tests cover:
- Correct hashing of individual items
- Tree construction for various sizes
- Proof generation and verification
- Edge cases (empty, single, large)
- Serialization round-trip
- No circular references (via `sys.getrefcount` and `weakref`)
- Consistency: same data always produces same root hash
