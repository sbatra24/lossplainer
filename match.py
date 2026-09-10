"""Play a match between two evaluators at fixed depth and write a report.

Openings are random and paired: each random opening is played twice with
colours swapped, which removes most of the first-move advantage noise.

Usage: python match.py --games 20 --depth 2 --opponent init
       python match.py --games 20 --depth 2 --opponent material
"""
from __future__ import annotations

import argparse
import math
import multiprocessing as mp
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from board import Board
from eval import DEFAULT_WEIGHTS, EvalNet, MaterialEval
from explain import material_summary
from search import Limits, Searcher

os.environ.setdefault("OMP_NUM_THREADS", "1")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


@dataclass
class GameResult:
    opening: str          # SAN of the random opening moves
    trained_is_white: bool
    result: str           # "1-0", "0-1", "1/2-1/2"
    plies: int
    reason: str
    final_material: str   # from the trained side's view

    @property
    def trained_points(self) -> float:
        if self.result == "1/2-1/2":
            return 0.5
        return 1.0 if (self.result == "1-0") == self.trained_is_white else 0.0


def make_opponent(kind: str) -> object:
    if kind == "init":
        return EvalNet.initial()
    if kind == "material":
        return MaterialEval()
    return EvalNet.load(kind)


def play(trained_params: Dict[str, np.ndarray], opponent_kind: str, opening_seed: int,
         trained_is_white: bool, depth: int, max_plies: int) -> GameResult:
    rng = random.Random(opening_seed)
    board = Board()
    opening_sans: List[str] = []
    for _ in range(rng.randint(4, 8)):
        moves = board.legal_moves()
        m = rng.choice(moves)
        opening_sans.append(board.san(m))
        board.make(m)
    trained = Searcher(EvalNet(trained_params))
    other = Searcher(make_opponent(opponent_kind))
    white, black = (trained, other) if trained_is_white else (other, trained)
    plies = 0
    reason = "truncated at move limit"
    while plies < max_plies:
        outcome = board.result()
        if outcome is not None:
            if board.is_checkmate():
                reason = "checkmate"
            elif board.is_stalemate():
                reason = "stalemate"
            elif board.is_threefold():
                reason = "threefold repetition"
            elif board.is_fifty_moves():
                reason = "fifty-move rule"
            else:
                reason = "insufficient material"
            break
        searcher = white if board.side == 1 else black
        res = searcher.search(board, Limits(depth=depth, seconds=10.0))
        board.make(res.best_move)
        plies += 1
    outcome = board.result() or "1/2-1/2"
    trained_side = 1 if trained_is_white else -1
    mat, _ = material_summary(board, trained_side)
    return GameResult(" ".join(opening_sans), trained_is_white, outcome, plies, reason, mat)


def _worker(args: Tuple) -> GameResult:
    return play(*args)


def elo_estimate(score: float, n: int) -> Tuple[float, float]:
    """Elo difference implied by a match score, with a 95% half-width (normal approx)."""
    p = min(max(score / n, 1e-3), 1 - 1e-3)
    elo = -400.0 * math.log10(1.0 / p - 1.0)
    se = math.sqrt(p * (1 - p) / n)
    lo = min(max(p - 1.96 * se, 1e-3), 1 - 1e-3)
    hi = min(max(p + 1.96 * se, 1e-3), 1 - 1e-3)
    half = (-400.0 * math.log10(1.0 / hi - 1.0) - -400.0 * math.log10(1.0 / lo - 1.0)) / 2.0
    return elo, half


def run_match(weights: str, opponent: str, games: int, depth: int, workers: int, seed: int,
              max_plies: int = 200) -> Tuple[List[GameResult], float]:
    trained = EvalNet.load(weights)
    params = trained.params()
    rng = random.Random(seed)
    jobs = []
    for pair in range(games // 2):
        opening_seed = rng.randrange(2**31)
        jobs.append((params, opponent, opening_seed, True, depth, max_plies))
        jobs.append((params, opponent, opening_seed, False, depth, max_plies))
    start = time.time()
    with mp.get_context("fork").Pool(workers) as pool:
        results = pool.map(_worker, jobs)
    return results, time.time() - start


def report(results: List[GameResult], opponent: str, depth: int, seconds: float) -> str:
    n = len(results)
    score = sum(r.trained_points for r in results)
    wins = sum(1 for r in results if r.trained_points == 1.0)
    draws = sum(1 for r in results if r.trained_points == 0.5)
    losses = n - wins - draws
    elo, half = elo_estimate(score, n)
    opp_name = {"init": "untrained network (material + piece-square tables)",
                "material": "pure material count"}.get(opponent, opponent)
    lines = [
        f"## Trained network vs {opp_name}",
        "",
        f"Fixed depth {depth} plus quiescence, {n} games with paired random openings, "
        f"{seconds / 60:.1f} minutes of wall time on 2 cores.",
        "",
        f"Score for the trained network: **{score:g} / {n}** "
        f"({wins} wins, {draws} draws, {losses} losses, {100 * score / n:.0f}%).",
        f"Implied Elo difference: about {elo:+.0f} with a 95% interval of roughly +-{half:.0f} "
        f"(a normal approximation; {n} games is a small sample).",
        "",
        "| game | trained plays | opening | result | plies | ended by | final material (trained side) |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(results, 1):
        lines.append(f"| {i} | {'White' if r.trained_is_white else 'Black'} | {r.opening} | {r.result} | "
                     f"{r.plies} | {r.reason} | {r.final_material} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--weights", default=DEFAULT_WEIGHTS)
    ap.add_argument("--opponent", default="init", help="'init', 'material', or a path to another .npz")
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(OUT_DIR, "match_results.md"))
    ap.add_argument("--append", action="store_true")
    args = ap.parse_args()
    results, seconds = run_match(args.weights, args.opponent, args.games, args.depth, args.workers, args.seed)
    text = report(results, args.opponent, args.depth, seconds)
    with open(args.out, "a" if args.append else "w") as f:
        if not args.append:
            f.write("# Match results\n\n")
        f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
