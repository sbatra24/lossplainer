"""Play against the engine in the terminal; it explains itself after every move.

Usage: python play.py [--color white|black] [--depth 4] [--seconds 5] [--fen FEN]

Type moves in SAN (Nf3, exd5, O-O, e8=Q) or UCI (g1f3).  Other commands:
  why      explain what the engine thinks of the current position, from your side
  wrong    the "what did my first impression get wrong" analysis of the current position
  undo     take back the last move pair
  fen      print the FEN
  quit
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from board import BLACK, WHITE, Board, move_to_uci
from eval import DEFAULT_WEIGHTS, load_or_initial
from explain import contribution_table, explain, explain_discrepancy
from search import Searcher, score_text


def engine_turn(board: Board, searcher: Searcher, net, depth: int, seconds: Optional[float],
                verbose: bool) -> None:
    ex = explain(board, net, depth=depth, seconds=seconds, searcher=searcher)
    res = ex.result
    san = board.san(res.best_move)
    print(f"\nEngine plays {san} ({move_to_uci(res.best_move)})  "
          f"[depth {res.depth}, {res.nodes} nodes, {res.nps:.0f} nodes/s, eval {score_text(res.score)}]")
    print(ex.text)
    if verbose:
        print()
        print(contribution_table(ex.contributions, 8))
    board.make(res.best_move)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--color", choices=["white", "black"], default="white", help="your colour")
    ap.add_argument("--depth", type=int, default=4)
    ap.add_argument("--seconds", type=float, default=None, help="soft time limit per engine move")
    ap.add_argument("--fen", default=None)
    ap.add_argument("--weights", default=DEFAULT_WEIGHTS)
    ap.add_argument("--verbose", action="store_true", help="also print the attribution table")
    args = ap.parse_args()

    net = load_or_initial(args.weights)
    searcher = Searcher(net)
    board = Board(args.fen) if args.fen else Board()
    human = WHITE if args.color == "white" else BLACK
    print(__doc__)
    while True:
        print()
        print(board)
        outcome = board.result()
        if outcome is not None:
            print(f"Game over: {outcome}")
            break
        if board.side != human:
            engine_turn(board, searcher, net, args.depth, args.seconds, args.verbose)
            continue
        try:
            text = input("your move> ").strip()
        except EOFError:
            break
        if not text:
            continue
        if text == "quit":
            break
        if text == "fen":
            print(board.fen())
            continue
        if text == "undo":
            for _ in range(2):
                if board._stack:
                    board.unmake()
            continue
        if text == "why":
            ex = explain(board, net, depth=args.depth, seconds=args.seconds, searcher=searcher)
            print("Speaking from your side of the board:")
            print(ex.text)
            if args.verbose:
                print(contribution_table(ex.contributions, 8))
            continue
        if text == "wrong":
            print(explain_discrepancy(board, net, depth=args.depth, seconds=args.seconds, searcher=searcher).text)
            continue
        move = board.parse_san(text)
        if move is None:
            print("Not a legal move. Try SAN like Nf3 or UCI like g1f3.")
            continue
        board.make(move)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
