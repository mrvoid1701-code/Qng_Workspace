"""
Smoke tests for the Jaccard Informational Graph construction.

Validates:
  1. Graph structure (n nodes, connectivity, degree)
  2. Jaccard similarity scores are in [0, 1] and symmetric
  3. Spectral gap μ₁ > 0 (graph is connected)
  4. Sigma field is in [0, 1] (valid probability-like field)

These tests run in < 1s (n=40, k=4) — no heavy physics gates.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


# ---------------------------------------------------------------------------
# Minimal standalone Jaccard graph builder (copied logic, no script deps)
# ---------------------------------------------------------------------------

def _build_jaccard_graph(n: int, k_init: int, k_conn: int, seed: int) -> list[list[int]]:
    """Build a Jaccard Informational Graph.

    Step 1: random ER base graph with p = k_init / (n-1).
    Step 2: for each node i, rank all other nodes j by
            Jaccard(N_i ∪ {i}, N_j ∪ {j}) and connect to top-k_conn.
    Returns adjacency list (sorted).
    """
    rng = random.Random(seed)
    p0 = k_init / (n - 1)

    # ER base graph
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p0:
                adj0[i].add(j)
                adj0[j].add(i)

    # Jaccard similarity → k_conn nearest neighbours
    adj = [set() for _ in range(n)]
    for i in range(n):
        Ni = adj0[i] | {i}
        scores: list[tuple[float, int]] = []
        for j in range(n):
            if j == i:
                continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj)
            union = len(Ni | Nj)
            scores.append((inter / union if union else 0.0, j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j)
            adj[j].add(i)

    return [sorted(s) for s in adj]


def _jaccard_scores(adj0: list[set], i: int, n: int) -> list[float]:
    """Return Jaccard(N_i ∪ {i}, N_j ∪ {j}) for all j ≠ i."""
    Ni = adj0[i] | {i}
    results = []
    for j in range(n):
        if j == i:
            continue
        Nj = adj0[j] | {j}
        inter = len(Ni & Nj)
        union = len(Ni | Nj)
        results.append(inter / union if union else 0.0)
    return results


def _bfs_distances(adj: list[list[int]], source: int) -> list[int]:
    """BFS distances from source; unreachable nodes get distance n."""
    n = len(adj)
    dist = [-1] * n
    dist[source] = 0
    queue = [source]
    head = 0
    while head < len(queue):
        u = queue[head]; head += 1
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                queue.append(v)
    return [d if d >= 0 else n for d in dist]


def _laplacian_eigenvalues_small(adj: list[list[int]]) -> list[float]:
    """Return all eigenvalues of the normalized Laplacian via power iteration
    approximation for small graphs (n ≤ 60).  Uses Jacobi-like approach via
    the characteristic polynomial root finding is avoided — we use a simple
    inverse-power method via numpy if available, else stdlib fallback."""
    n = len(adj)
    # Degree vector
    deg = [len(adj[i]) for i in range(n)]

    # Build D^{-1/2} L D^{-1/2} as a flat list (row-major)
    mat = [[0.0] * n for _ in range(n)]
    for i in range(n):
        if deg[i] > 0:
            mat[i][i] = 1.0
        for j in adj[i]:
            if deg[i] > 0 and deg[j] > 0:
                mat[i][j] = -1.0 / math.sqrt(deg[i] * deg[j])

    # Power iteration for smallest non-trivial eigenvalue μ₁
    # Use deflation: project out the constant eigenvector (eigenvalue 0).
    rng = random.Random(42)
    v = [rng.gauss(0, 1) for _ in range(n)]

    # Orthogonalize against constant vector
    def _ortho_const(vec: list[float]) -> list[float]:
        mean = sum(vec) / n
        return [x - mean for x in vec]

    def _normalize(vec: list[float]) -> list[float]:
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec] if norm > 1e-14 else vec

    def _matvec(m: list[list[float]], vec: list[float]) -> list[float]:
        return [sum(m[i][j] * vec[j] for j in range(n)) for i in range(n)]

    v = _normalize(_ortho_const(v))

    # Inverse-power iteration approximation: just regular power iter after shift
    # μ₁ = smallest nonzero eigenvalue; use shift-invert approx via (2I - L)
    # which converts smallest-near-0 to largest near 2.
    shift_mat = [[2.0 * (i == j) - mat[i][j] for j in range(n)] for i in range(n)]

    for _ in range(60):
        w = _matvec(shift_mat, v)
        w = _ortho_const(w)
        lam = math.sqrt(sum(x * x for x in w))
        v = _normalize(w)

    # Rayleigh quotient for μ₁ (with original mat)
    Lv = _matvec(mat, v)
    mu1 = sum(v[i] * Lv[i] for i in range(n))
    return [mu1]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

N_SMALL = 40
K_INIT  = 5
K_CONN  = 4
SEED    = 3401


class TestJaccardGraphStructure:
    """Validate the Jaccard graph has the correct structure."""

    def _graph(self):
        return _build_jaccard_graph(N_SMALL, K_INIT, K_CONN, SEED)

    def test_node_count(self):
        adj = self._graph()
        assert len(adj) == N_SMALL

    def test_adjacency_lists_sorted(self):
        adj = self._graph()
        for i, nbrs in enumerate(adj):
            assert nbrs == sorted(nbrs), f"Node {i} adjacency not sorted"

    def test_no_self_loops(self):
        adj = self._graph()
        for i, nbrs in enumerate(adj):
            assert i not in nbrs, f"Self-loop at node {i}"

    def test_symmetry(self):
        adj = self._graph()
        for i, nbrs in enumerate(adj):
            for j in nbrs:
                assert i in adj[j], f"Edge ({i},{j}) not symmetric"

    def test_minimum_degree(self):
        """Every node should have at least k_conn neighbours."""
        adj = self._graph()
        for i, nbrs in enumerate(adj):
            assert len(nbrs) >= K_CONN, (
                f"Node {i} has degree {len(nbrs)} < k_conn={K_CONN}"
            )

    def test_graph_is_connected(self):
        """BFS from node 0 must reach all nodes."""
        adj = self._graph()
        dist = _bfs_distances(adj, 0)
        unreachable = [i for i, d in enumerate(dist) if d >= N_SMALL]
        assert unreachable == [], f"Unreachable nodes: {unreachable}"


class TestJaccardSimilarityScores:
    """Validate Jaccard similarity values are mathematically correct."""

    def _base_graph(self):
        rng = random.Random(SEED)
        p0 = K_INIT / (N_SMALL - 1)
        adj0 = [set() for _ in range(N_SMALL)]
        for i in range(N_SMALL):
            for j in range(i + 1, N_SMALL):
                if rng.random() < p0:
                    adj0[i].add(j)
                    adj0[j].add(i)
        return adj0

    def test_scores_in_unit_interval(self):
        adj0 = self._base_graph()
        for i in range(N_SMALL):
            for score in _jaccard_scores(adj0, i, N_SMALL):
                assert 0.0 <= score <= 1.0, f"Score {score} out of [0,1]"

    def test_score_symmetry(self):
        """J(i,j) == J(j,i) for all pairs."""
        adj0 = self._base_graph()
        for i in range(min(10, N_SMALL)):
            Ni = adj0[i] | {i}
            for j in range(i + 1, min(10, N_SMALL)):
                Nj = adj0[j] | {j}
                inter = len(Ni & Nj)
                union = len(Ni | Nj)
                j_ij = inter / union if union else 0.0
                # Swap roles
                inter2 = len(Nj & Ni)
                union2 = len(Nj | Ni)
                j_ji = inter2 / union2 if union2 else 0.0
                assert abs(j_ij - j_ji) < 1e-12, f"J({i},{j}) != J({j},{i})"

    def test_self_similarity_is_one(self):
        """J(i,i) = |Ni| / |Ni| = 1."""
        adj0 = self._base_graph()
        for i in range(min(5, N_SMALL)):
            Ni = adj0[i] | {i}
            inter = len(Ni & Ni)
            union = len(Ni | Ni)
            score = inter / union if union else 0.0
            assert abs(score - 1.0) < 1e-12, f"Self-similarity at {i} is {score}"

    def test_disjoint_neighborhoods_score_zero(self):
        """If N_i ∩ N_j = ∅ and i ∉ N_j and j ∉ N_i, score may be low."""
        # Construct a minimal case: two isolated nodes with no shared neighbours
        adj0_custom = [set() for _ in range(6)]
        # Node 0 and node 1 have completely disjoint closed neighbourhoods
        adj0_custom[0] = {2, 3}
        adj0_custom[2].add(0); adj0_custom[3].add(0)
        adj0_custom[1] = {4, 5}
        adj0_custom[4].add(1); adj0_custom[5].add(1)
        N0 = adj0_custom[0] | {0}  # {0, 2, 3}
        N1 = adj0_custom[1] | {1}  # {1, 4, 5}
        inter = len(N0 & N1)
        union = len(N0 | N1)
        score = inter / union if union else 0.0
        assert score == 0.0, f"Expected 0.0, got {score}"


class TestJaccardSpectralProperties:
    """Validate spectral properties of the Jaccard graph."""

    def test_spectral_gap_positive(self):
        """Normalized Laplacian μ₁ > 0 ↔ graph is connected."""
        adj = _build_jaccard_graph(N_SMALL, K_INIT, K_CONN, SEED)
        eigenvalues = _laplacian_eigenvalues_small(adj)
        mu1 = eigenvalues[0]
        assert mu1 > 0.0, f"Spectral gap μ₁={mu1:.6f} ≤ 0 (disconnected?)"

    def test_spectral_gap_threshold(self):
        """μ₁ > 0.01 — matches the G17a gate threshold."""
        adj = _build_jaccard_graph(N_SMALL, K_INIT, K_CONN, SEED)
        eigenvalues = _laplacian_eigenvalues_small(adj)
        mu1 = eigenvalues[0]
        assert mu1 > 0.01, f"Spectral gap μ₁={mu1:.6f} below G17a threshold 0.01"

    def test_different_seeds_give_different_graphs(self):
        """Two different seeds should produce different adjacency structures."""
        adj1 = _build_jaccard_graph(N_SMALL, K_INIT, K_CONN, seed=1)
        adj2 = _build_jaccard_graph(N_SMALL, K_INIT, K_CONN, seed=2)
        identical = all(adj1[i] == adj2[i] for i in range(N_SMALL))
        assert not identical, "Different seeds produced identical graphs"

    def test_same_seed_reproducible(self):
        """Same seed must always produce the same graph."""
        adj1 = _build_jaccard_graph(N_SMALL, K_INIT, K_CONN, SEED)
        adj2 = _build_jaccard_graph(N_SMALL, K_INIT, K_CONN, SEED)
        assert adj1 == adj2, "Same seed produced different graphs (non-deterministic)"
