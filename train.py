"""Self-play training of the evaluation network with TD-Leaf(lambda).

Each game is played by the engine against itself at a fixed search depth.
For every move we keep the feature vector of the principal variation's
leaf (the position whose static evaluation became the search score).  After
the game, the leaf evaluations are trained toward the TD(lambda) return of
the later search scores, with the game result as the terminal value.  That
is TD-Leaf as described by Baxter, Tridgell and Weaver for KnightCap.

Usage: python train.py --minutes 30 --depth 2 --workers 2
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from board import Board
from eval import EvalNet
from features import extract, swap_perspective
from search import Limits, Searcher

os.environ.setdefault("OMP_NUM_THREADS", "1")

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
TERMINAL_VALUE = 8.0     # pawns credited for a won game
CLIP = 10.0              # targets are clipped to +-CLIP pawns


@dataclass
class GameRecord:
    leaf_features: List[np.ndarray]   # one per move, from the mover's perspective
    scores: List[float]               # search score per move, in pawns, mover's perspective
    sides: List[int]                  # side to move per ply (+1 white, -1 black)
    breaks: List[bool]                # True where the move played was random (trajectory break)
    result: str                       # "1-0", "0-1", "1/2-1/2" or "*" (truncated)
    plies: int
    final_value_white: float          # terminal value in pawns from White's view


def play_game(params: Dict[str, np.ndarray], seed: int, depth: int, max_plies: int,
              random_opening_plies: int, epsilon: float) -> GameRecord:
    """Play one self-play game and record the TD-Leaf training data."""
    rng = random.Random(seed)
    net = EvalNet(params)
    searcher = Searcher(net)
    board = Board()
    rec = GameRecord([], [], [], [], "*", 0, 0.0)

    # Random opening moves for diversity (not recorded).
    for _ in range(random_opening_plies):
        moves = board.legal_moves()
        if not moves or board.result() is not None:
            break
        board.make(rng.choice(moves))

    last_score_white = 0.0
    while board.result() is None and rec.plies < max_plies:
        result = searcher.search(board, Limits(depth=depth, seconds=3.0))
        leaf = board.copy()
        for m in result.pv:
            leaf.make(m)
        x, _ = extract(leaf)
        if leaf.side != board.side:
            x = swap_perspective(x)
        score = float(np.clip(result.score / 100.0, -CLIP, CLIP))
        rec.leaf_features.append(x)
        rec.scores.append(score)
        rec.sides.append(board.side)
        explore = rng.random() < epsilon
        rec.breaks.append(explore)
        last_score_white = score * board.side
        move = rng.choice(board.legal_moves()) if explore else result.best_move
        board.make(move)
        rec.plies += 1

    outcome = board.result()
    if outcome == "1-0":
        rec.final_value_white = TERMINAL_VALUE
    elif outcome == "0-1":
        rec.final_value_white = -TERMINAL_VALUE
    elif outcome == "1/2-1/2":
        rec.final_value_white = 0.0
    else:
        rec.final_value_white = last_score_white  # truncated game: bootstrap from the last search
    rec.result = outcome or "*"
    return rec


def td_lambda_targets(rec: GameRecord, lam: float) -> Tuple[np.ndarray, np.ndarray]:
    """TD(lambda) returns for each recorded leaf, in the mover's perspective.

    Values are converted to White's view, the lambda-return is accumulated
    backwards from the terminal value, and trajectories are cut at random
    (exploratory) moves so the evaluation is not blamed for them.
    """
    n = len(rec.scores)
    v_white = np.array([s * side for s, side in zip(rec.scores, rec.sides)])
    targets_white = np.empty(n)
    next_value = rec.final_value_white
    for t in range(n - 1, -1, -1):
        if rec.breaks[t]:
            # The move after this position was random: no information about
            # what the evaluation should have been.  Use its own value.
            targets_white[t] = v_white[t]
            next_value = v_white[t]
            continue
        # lambda-return: G_t = (1-lam) * v_{t+1} + lam * G_{t+1}, bootstrapping on v_{t+1}.
        if t == n - 1:
            g = next_value
        else:
            g = (1.0 - lam) * v_white[t + 1] + lam * next_value
        targets_white[t] = g
        next_value = g
    targets = np.clip(targets_white * np.array(rec.sides), -CLIP, CLIP)
    return np.stack(rec.leaf_features), targets


class Adam:
    """Plain Adam optimiser over a dict of parameter arrays."""

    def __init__(self, shapes: Dict[str, Tuple[int, ...]], lr: float, beta1: float = 0.9,
                 beta2: float = 0.999, eps: float = 1e-8) -> None:
        self.lr, self.b1, self.b2, self.eps = lr, beta1, beta2, eps
        self.m = {k: np.zeros(s) for k, s in shapes.items()}
        self.v = {k: np.zeros(s) for k, s in shapes.items()}
        self.t = 0

    def step(self, grads: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        self.t += 1
        out: Dict[str, np.ndarray] = {}
        for k, g in grads.items():
            self.m[k] = self.b1 * self.m[k] + (1 - self.b1) * g
            self.v[k] = self.b2 * self.v[k] + (1 - self.b2) * g * g
            m_hat = self.m[k] / (1 - self.b1 ** self.t)
            v_hat = self.v[k] / (1 - self.b2 ** self.t)
            out[k] = -self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
        return out


def _worker(args: Tuple[Dict[str, np.ndarray], int, int, int, int, float]) -> GameRecord:
    return play_game(*args)


def train(minutes: float, depth: int, workers: int, seed: int, lam: float, lr: float,
          epsilon: float, out_dir: str, games_per_iter: Optional[int] = None,
          max_plies: int = 160, replay_size: int = 6000) -> EvalNet:
    os.makedirs(out_dir, exist_ok=True)
    net = EvalNet.initial(seed=seed)
    optimiser = Adam({k: v.shape for k, v in net.params().items() if k != "scale"}, lr=lr)
    rng = np.random.default_rng(seed)
    games_per_iter = games_per_iter or 2 * workers
    log_path = os.path.join(out_dir, "training_log.jsonl")
    txt_path = os.path.join(out_dir, "training_log.txt")
    start = time.time()
    deadline = start + minutes * 60.0
    replay_x: List[np.ndarray] = []
    replay_y: List[np.ndarray] = []
    total_games = 0
    total_positions = 0
    w_d_l = [0, 0, 0]
    initial = net.copy()
    header = (f"TD-Leaf self-play training: depth={depth} lambda={lam} lr={lr} epsilon={epsilon} "
              f"workers={workers} budget={minutes:.0f} min seed={seed}\n")
    with open(txt_path, "w") as txt, open(log_path, "w") as jl:
        txt.write(header)
        txt.write("iter  games  positions  avg_plies  W/D/L(this iter)   mean|TD|   loss_before  loss_after  |dW|     elapsed\n")
        txt.flush()
        ctx = mp.get_context("fork")
        iteration = 0
        with ctx.Pool(workers) as pool:
            while time.time() < deadline:
                iteration += 1
                params = net.params()
                jobs = [(params, int(rng.integers(0, 2**31)), depth, max_plies,
                         int(rng.integers(2, 9)), epsilon) for _ in range(games_per_iter)]
                records = pool.map(_worker, jobs)
                xs, ys, tds = [], [], []
                wdl = [0, 0, 0]
                plies = 0
                for rec in records:
                    if not rec.scores:
                        continue
                    X, y = td_lambda_targets(rec, lam)
                    xs.append(X)
                    ys.append(y)
                    tds.append(np.abs(y - np.array(rec.scores)))
                    plies += rec.plies
                    wdl[{"1-0": 0, "1/2-1/2": 1, "0-1": 2, "*": 1}[rec.result]] += 1
                if not xs:
                    continue
                X_new = np.concatenate(xs)
                y_new = np.concatenate(ys)
                replay_x.append(X_new)
                replay_y.append(y_new)
                while sum(len(a) for a in replay_x) > replay_size and len(replay_x) > 1:
                    replay_x.pop(0)
                    replay_y.pop(0)
                X = np.concatenate(replay_x)
                y = np.concatenate(replay_y)
                # Weight recent positions more heavily than replayed ones.
                w = np.concatenate([np.full(len(a), 0.5) for a in replay_x[:-1]] + [np.ones(len(X_new))])
                loss_before, _ = net.loss_and_grads(X, y, w)
                before = net.params()
                n = len(X)
                batch = 256
                order = rng.permutation(n)
                for i in range(0, n, batch):
                    idx = order[i:i + batch]
                    _, grads = net.loss_and_grads(X[idx], y[idx], w[idx])
                    # Clip gradient norm for stability.
                    norm = float(np.sqrt(sum(float((g * g).sum()) for g in grads.values())))
                    if norm > 5.0:
                        grads = {k: g * (5.0 / norm) for k, g in grads.items()}
                    net.apply_update(optimiser.step(grads))
                loss_after, _ = net.loss_and_grads(X, y, w)
                dw = float(np.sqrt(sum(float(((net.params()[k] - before[k]) ** 2).sum())
                                       for k in before if k != "scale")))
                total_games += len(records)
                total_positions += len(X_new)
                for i in range(3):
                    w_d_l[i] += wdl[i]
                elapsed = time.time() - start
                mean_td = float(np.mean(np.concatenate(tds)))
                row = {"iter": iteration, "games": total_games, "positions": total_positions,
                       "avg_plies": plies / max(1, len(records)), "wdl_iter": wdl,
                       "mean_abs_td": mean_td, "loss_before": loss_before, "loss_after": loss_after,
                       "weight_change": dw, "elapsed_s": elapsed}
                jl.write(json.dumps(row) + "\n")
                jl.flush()
                txt.write(f"{iteration:4d}  {total_games:5d}  {total_positions:9d}  {plies / max(1, len(records)):9.1f}  "
                          f"{wdl[0]}/{wdl[1]}/{wdl[2]:<13}   {mean_td:7.3f}   {loss_before:11.4f}  {loss_after:10.4f}  "
                          f"{dw:6.3f}   {elapsed / 60:6.1f} min\n")
                txt.flush()
                net.save(os.path.join(out_dir, "eval_net.npz"))
        drift = float(np.sqrt(sum(float(((net.params()[k] - initial.params()[k]) ** 2).sum())
                                  for k in ("w_lin", "W1", "b1", "W2"))))
        txt.write(f"\nDone: {total_games} games, {total_positions} training positions, "
                  f"{(time.time() - start) / 60:.1f} minutes. "
                  f"Game results (white wins/draws or truncated/black wins): {w_d_l[0]}/{w_d_l[1]}/{w_d_l[2]}. "
                  f"Total weight drift from initialisation: {drift:.3f}\n")
    net.save(os.path.join(out_dir, "eval_net.npz"))
    return net


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--minutes", type=float, default=30.0)
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--lam", type=float, default=0.7)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--epsilon", type=float, default=0.05, help="probability of a random exploratory move")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()
    train(args.minutes, args.depth, args.workers, args.seed, args.lam, args.lr, args.epsilon, args.out)
    print(f"saved {os.path.join(args.out, 'eval_net.npz')}")


if __name__ == "__main__":
    main()
