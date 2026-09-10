"""Evaluation network: a small NumPy MLP over the named features.

    g(x)     = x . w_lin + W2 . tanh(W1 . (x / scale) + b1)
    score(x) = g(x) - g(swap(x))

where ``swap`` exchanges the side-to-move and opponent feature blocks.  The
subtraction makes the network exactly antisymmetric: the same position
scores +s from one side and -s from the other, and an empty feature vector
scores 0, which is what makes attributions sum cleanly.

The linear skip term is initialised to half the classical material +
piece-square evaluation (the subtraction doubles it) and the hidden layer's
output weights start at zero, so a fresh network is exactly the hand-tuned
baseline.  Self-play training (``train.py``) then adjusts every weight.

Scores are in pawns from the side to move's point of view.  ``evaluate``
converts to integer centipawns for the search.
"""
from __future__ import annotations

import os
from typing import Dict, Optional, Tuple

import numpy as np

from board import Board
from features import (FEATURE_NAMES, INIT_WEIGHTS, NUM_FEATURES, PERSPECTIVE_PERM,
                      PERSPECTIVE_SIGN, extract, swap_perspective)

HIDDEN = 32
DEFAULT_WEIGHTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "eval_net.npz")

# Rough scale of each feature so hidden-layer inputs are O(1).  These are
# constants, chosen by feature type rather than fitted, so that a saved
# network is fully described by its weights.
_SCALE_BY_PREFIX = {
    "material_total": 40.0, "pawns": 8.0, "knights": 2.0, "bishops": 2.0, "rooks": 2.0, "queens": 1.0,
    "knight_mobility": 16.0, "bishop_mobility": 16.0, "rook_mobility": 20.0, "queen_mobility": 25.0,
    "king_pawn_shield": 3.0, "king_open_files": 3.0, "king_zone_attackers": 4.0, "king_zone_attacks": 8.0,
    "castling_rights": 2.0, "pawn_storm": 3.0, "doubled_pawns": 2.0, "isolated_pawns": 3.0,
    "backward_pawns": 2.0, "connected_pawns": 6.0, "pawn_islands": 4.0, "passed_pawns": 2.0,
    "passed_advancement": 8.0, "best_passer_rank": 5.0, "pawns_advanced": 4.0, "rook_open_file": 2.0,
    "rook_semi_open_file": 2.0, "bad_bishop_pawns": 8.0, "minors_undeveloped": 4.0, "hanging_pieces": 2.0,
    "attacked_by_lower": 2.0, "pinned_pieces": 2.0, "pawn_threats": 2.0, "center_control": 8.0,
    "center_pawns": 2.0, "space": 12.0, "king_centralization": 3.0, "king_pawn_distance": 4.0,
    "material_balance": 10.0,
}


def _feature_scale() -> np.ndarray:
    scale = np.ones(NUM_FEATURES, dtype=np.float64)
    for i, name in enumerate(FEATURE_NAMES):
        for prefix, s in _SCALE_BY_PREFIX.items():
            if name == prefix or name.startswith(prefix + "_"):
                scale[i] = s
    return scale


class EvalNet:
    """MLP evaluation with hand-computable forward, backward and input gradients."""

    def __init__(self, params: Dict[str, np.ndarray]) -> None:
        self.w_lin: np.ndarray = params["w_lin"].astype(np.float64)
        self.W1: np.ndarray = params["W1"].astype(np.float64)
        self.b1: np.ndarray = params["b1"].astype(np.float64)
        self.W2: np.ndarray = params["W2"].astype(np.float64)
        self.scale: np.ndarray = params["scale"].astype(np.float64)
        self._cache: Dict[int, float] = {}

    # ------------------------------------------------------------ factory

    @classmethod
    def initial(cls, hidden: int = HIDDEN, seed: int = 0) -> "EvalNet":
        """A network that computes exactly material + piece-square tables."""
        rng = np.random.default_rng(seed)
        return cls({
            "w_lin": INIT_WEIGHTS / 2.0,
            "W1": rng.normal(0.0, 0.3, size=(hidden, NUM_FEATURES)),
            "b1": np.zeros(hidden),
            "W2": np.zeros(hidden),
            "scale": _feature_scale(),
        })

    @classmethod
    def load(cls, path: str = DEFAULT_WEIGHTS) -> "EvalNet":
        with np.load(path, allow_pickle=False) as data:
            names = list(data["feature_names"])
            if names != FEATURE_NAMES:
                raise ValueError("weights were trained on a different feature registry")
            return cls({k: data[k] for k in ("w_lin", "W1", "b1", "W2", "scale")})

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        np.savez(path, w_lin=self.w_lin, W1=self.W1, b1=self.b1,
                 W2=self.W2, scale=self.scale, feature_names=np.array(FEATURE_NAMES))

    def copy(self) -> "EvalNet":
        return EvalNet(self.params())

    def params(self) -> Dict[str, np.ndarray]:
        return {"w_lin": self.w_lin.copy(), "W1": self.W1.copy(),
                "b1": self.b1.copy(), "W2": self.W2.copy(), "scale": self.scale.copy()}

    # ------------------------------------------------------------ forward

    def _g(self, x: np.ndarray) -> np.ndarray:
        h = np.tanh((x / self.scale) @ self.W1.T + self.b1)
        return x @ self.w_lin + h @ self.W2

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Score in pawns for a feature vector or a batch (rows) of them."""
        return self._g(x) - self._g(swap_perspective(x))

    def __call__(self, x: np.ndarray) -> float:
        return float(self.forward(x))

    def _g_input_gradient(self, x: np.ndarray) -> np.ndarray:
        h = np.tanh((x / self.scale) @ self.W1.T + self.b1)
        dh = (1.0 - h * h) * self.W2  # (..., hidden)
        return self.w_lin + (dh @ self.W1) / self.scale

    def input_gradient(self, x: np.ndarray) -> np.ndarray:
        """d score / d x for a vector or batch of feature vectors."""
        gx = self._g_input_gradient(x)
        gs = self._g_input_gradient(swap_perspective(x)) * PERSPECTIVE_SIGN
        # Chain rule through the permutation: d g(swap x)/d x_j = sign_i * gs_i where perm_i == j.
        back = np.empty_like(gs)
        back[..., PERSPECTIVE_PERM] = gs
        return gx - back

    # ------------------------------------------------------------ training

    def _g_grads(self, X: np.ndarray, d_out: np.ndarray) -> Dict[str, np.ndarray]:
        """Parameter gradients of sum_i d_out[i] * g(X[i])."""
        xs = X / self.scale
        h = np.tanh(xs @ self.W1.T + self.b1)
        d_h = np.outer(d_out, self.W2) * (1.0 - h * h)  # (n, hidden)
        return {"w_lin": X.T @ d_out, "W2": h.T @ d_out, "W1": d_h.T @ xs, "b1": d_h.sum(axis=0)}

    def loss_and_grads(self, X: np.ndarray, y: np.ndarray, weights: Optional[np.ndarray] = None
                       ) -> Tuple[float, Dict[str, np.ndarray]]:
        """Weighted mean squared error and parameter gradients on a batch."""
        n = X.shape[0]
        Xs = swap_perspective(X)
        out = self._g(X) - self._g(Xs)
        err = out - y
        w = np.ones(n) if weights is None else weights
        loss = float(np.mean(w * err * err))
        d_out = 2.0 * w * err / n
        g1 = self._g_grads(X, d_out)
        g2 = self._g_grads(Xs, d_out)
        return loss, {k: g1[k] - g2[k] for k in g1}

    def apply_update(self, deltas: Dict[str, np.ndarray]) -> None:
        self.w_lin += deltas["w_lin"]
        self.W1 += deltas["W1"]
        self.b1 += deltas["b1"]
        self.W2 += deltas["W2"]
        self._cache.clear()

    # ------------------------------------------------------------ search API

    def clear_cache(self) -> None:
        """Forget cached evaluations (used to get clean speed measurements)."""
        self._cache.clear()

    def evaluate(self, board: Board) -> int:
        """Integer centipawn score from the side to move's view (cached by hash)."""
        h = board.hash
        cached = self._cache.get(h)
        if cached is not None:
            return cached
        x, _ = extract(board)
        score = int(round(self.forward(x) * 100.0))
        if len(self._cache) > 200_000:
            self._cache.clear()
        self._cache[h] = score
        return score


class MaterialEval:
    """Pure material counting baseline (no positional terms at all)."""

    VALUES = {1: 100, 2: 320, 3: 330, 4: 500, 5: 900, 6: 0}

    def evaluate(self, board: Board) -> int:
        total = 0
        for _, p in board.pieces():
            v = self.VALUES[abs(p)]
            total += v if p > 0 else -v
        return total if board.side == 1 else -total


def load_or_initial(path: str = DEFAULT_WEIGHTS) -> EvalNet:
    """Load trained weights if present, otherwise the untrained initialisation."""
    if os.path.exists(path):
        return EvalNet.load(path)
    return EvalNet.initial()
