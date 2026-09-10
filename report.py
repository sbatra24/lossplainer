"""Generate the committed artefacts in ``outputs/`` from the actual code.

    python report.py bench      -> outputs/benchmarks.md   (perft, nodes/sec, depth timings)
    python report.py examples   -> outputs/examples.md     (famous positions, explained)
    python report.py selfgame   -> outputs/self_game.md    (engine vs itself, explanation per move)
"""
from __future__ import annotations

import argparse
import os
import platform
import time
from typing import List

from board import Board, perft
from eval import DEFAULT_WEIGHTS, EvalNet, load_or_initial
from explain import contribution_table, explain, explain_discrepancy
from features import NUM_FEATURES
from search import Limits, Searcher, pv_san, score_text

os.environ.setdefault("OMP_NUM_THREADS", "1")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

KIWIPETE = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"

EXAMPLES = [
    ("Greek gift: Colle vs O'Hanlon, Nice 1930, before 12.Bxh7+",
     "r1bqr1k1/pp1n1ppp/3bp3/8/3pB3/2P2N2/PP3PPP/R1BQR1K1 w - - 0 12",
     "The textbook bishop sacrifice on h7. Colle played 12.Bxh7+ Kxh7 13.Ng5+ and won. "
     "A depth-limited engine with a tiny network will not see the whole combination; "
     "the point is to read what it does and doesn't value here."),
    ("King and pawn endgame: king in front of its passed pawn",
     "8/5k2/8/3PK3/8/8/8/8 w - - 0 1",
     "White wins with the king ahead of the pawn. The only thing that matters is the passed pawn "
     "and the kings, so this is a clean test of the passed-pawn and king features."),
    ("Philidor position (rook endgame, Black holds the draw)",
     "4k3/7R/r7/4K3/4P3/8/8/8 b - - 0 1",
     "Black keeps the rook on the third rank until the pawn advances, then checks from behind. "
     "Theoretically drawn; the engine's search is far too shallow to know that, so the explanation "
     "shows what a material+structure network thinks a pawn-up rook endgame is worth."),
    ("Smothered mate pattern (Philidor's legacy): Qg8+ Rxg8, Nf7#",
     "r2q1r1k/pp4pp/4Q2N/8/8/8/PP3PPP/6K1 w - - 0 1",
     "A forced mate in two. This shows the explainer's short-circuit: when the search finds a mate "
     "the network's features are irrelevant and the engine says so, and the discrepancy mode "
     "reports that a static evaluation cannot see mates."),
    ("Kiwipete (the standard move-generator test position)",
     KIWIPETE,
     "A wild middlegame with every special move type available. Perft from here is how the move "
     "generator was validated; the explanation shows how the network weighs a messy position."),
]


def md_board(board: Board) -> str:
    return "```\n" + str(board) + "\n```"


def run_bench(net: EvalNet, out_path: str) -> None:
    lines = ["# Benchmarks", "",
             f"Measured on this machine: Python {platform.python_version()}, {platform.machine()}, "
             f"single thread. Numbers are from one run of `python report.py bench`.", "",
             "## Perft (legal move generator)", "",
             "| position | depth | nodes | seconds |", "|---|---|---|---|"]
    for name, fen, depths in (("start position", Board().fen(), (1, 2, 3, 4, 5)), ("Kiwipete", KIWIPETE, (1, 2, 3, 4))):
        b = Board(fen)
        for d in depths:
            t = time.perf_counter()
            n = perft(b, d)
            lines.append(f"| {name} | {d} | {n:,} | {time.perf_counter() - t:.2f} |")
    lines += ["", "## Search speed with the trained network", "",
              f"Feature extraction builds {NUM_FEATURES} named features per leaf in pure Python, so the "
              "node rate is low. Quiescence nodes are included in the count; every search starts with an "
              "empty transposition table and an empty evaluation cache.", "",
              "| position | depth | nodes | seconds | nodes/sec | score | principal variation |",
              "|---|---|---|---|---|---|---|"]
    positions = [("start position", Board().fen()), ("Kiwipete", KIWIPETE),
                 ("Italian middlegame", "r1bq1rk1/ppp2ppp/2n5/3p4/1bP5/2N2N2/PP2PPPP/R2QKB1R w KQ - 0 8"),
                 ("rook endgame", "2r3k1/pp3ppp/4p3/3pP3/3P4/2P2N2/P4PPP/2R3K1 b - - 0 20")]
    for name, fen in positions:
        for d in (3, 4, 5):
            b = Board(fen)
            net.clear_cache()
            res = Searcher(net).search(b, Limits(depth=d))
            lines.append(f"| {name} | {res.depth} | {res.nodes:,} | {res.seconds:.2f} | {res.nps:,.0f} | "
                         f"{score_text(res.score)} | {pv_san(b, res.pv)} |")
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def run_examples(net: EvalNet, depth: int, out_path: str) -> None:
    parts: List[str] = ["# Five famous positions, explained by the engine", "",
                        f"Every block below is the verbatim output of `explain()` and `explain_discrepancy()` "
                        f"at depth {depth} using `outputs/eval_net.npz`. Nothing is hand-edited.", ""]
    for title, fen, blurb in EXAMPLES:
        board = Board(fen)
        searcher = Searcher(net)
        ex = explain(board, net, depth=depth, searcher=searcher)
        disc = explain_discrepancy(board, net, depth=depth, searcher=searcher)
        who = "White" if board.side == 1 else "Black"
        parts += [f"## {title}", "", f"FEN: `{fen}`  ({who} to move, so \"I\" is {who})", "", md_board(board), "",
                  blurb, "",
                  f"Search: depth {ex.result.depth}, {ex.result.nodes:,} nodes in {ex.result.seconds:.1f}s "
                  f"({ex.result.nps:,.0f} nodes/s), score {score_text(ex.result.score)}.", "",
                  "### What the engine says", "", "> " + ex.text.replace("\n", "\n>\n> "), "",
                  "### What its first impression got wrong", "", "> " + disc.text.replace("\n", "\n>\n> "), ""]
        if not ex.result.is_mate():
            parts += ["### Top attributions at the end of the line (Integrated Gradients, pawns)", "",
                      "```", contribution_table(ex.contributions, 10), "```", "",
                      f"Completeness check: attributions sum to the network output with error "
                      f"{ex.completeness_error:.1e} ({ex.ig_steps} integration steps).", "",
                      "### Group ablation (score change when the group's features are zeroed)", "",
                      "```", "\n".join(f"{g:<16} {v:+.3f}" for g, v in sorted(ex.ablation.items(), key=lambda kv: -abs(kv[1]))),
                      "```", ""]
    with open(out_path, "w") as f:
        f.write("\n".join(parts))
    print("\n".join(parts))


def run_selfgame(net: EvalNet, depth: int, seconds: float, max_plies: int, out_path: str) -> None:
    board = Board()
    searcher = Searcher(net)
    parts: List[str] = ["# The engine plays itself and explains every move", "",
                        f"Trained network on both sides, depth {depth} with a {seconds:.0f}s soft limit per move. "
                        "Each explanation is the engine speaking as the side that just moved, about the position "
                        "it expects after its principal variation.", ""]
    sans: List[str] = []
    start = time.time()
    total_nodes = 0
    while board.result() is None and len(sans) < max_plies:
        ex = explain(board, net, depth=depth, seconds=seconds, searcher=searcher)
        res = ex.result
        total_nodes += res.nodes
        san = board.san(res.best_move)
        number = f"{board.fullmove}." if board.side == 1 else f"{board.fullmove}..."
        sans.append((number + " " if board.side == 1 else "") + san)
        parts += [f"### {number} {san}", "",
                  f"`{board.fen()}`  depth {res.depth}, {res.nodes:,} nodes, {res.nps:,.0f} n/s, eval {score_text(res.score)}",
                  "", "> " + ex.text.replace("\n", "\n>\n> "), ""]
        board.make(res.best_move)
    outcome = board.result() or "* (stopped at move limit)"
    movetext = " ".join(sans)
    parts.insert(4, f"Result: **{outcome}** after {len(sans)} plies, {total_nodes:,} nodes, "
                    f"{(time.time() - start) / 60:.1f} minutes.\n\n```\n{movetext}\n```\n")
    parts += [f"Final position: `{board.fen()}`", "", md_board(board), ""]
    with open(out_path, "w") as f:
        f.write("\n".join(parts))
    print(f"{outcome} in {len(sans)} plies -> {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["bench", "examples", "selfgame"])
    ap.add_argument("--weights", default=DEFAULT_WEIGHTS)
    ap.add_argument("--depth", type=int, default=4)
    ap.add_argument("--seconds", type=float, default=8.0)
    ap.add_argument("--max-plies", type=int, default=200)
    args = ap.parse_args()
    net = load_or_initial(args.weights)
    os.makedirs(OUT_DIR, exist_ok=True)
    if args.what == "bench":
        run_bench(net, os.path.join(OUT_DIR, "benchmarks.md"))
    elif args.what == "examples":
        run_examples(net, args.depth, os.path.join(OUT_DIR, "examples.md"))
    else:
        run_selfgame(net, args.depth, args.seconds, args.max_plies, os.path.join(OUT_DIR, "self_game.md"))


if __name__ == "__main__":
    main()
