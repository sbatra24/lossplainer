"""UCI front end so the engine can be loaded into any chess GUI.

Supported: uci, isready, ucinewgame, setoption name Explain value true|false,
position [startpos | fen <fen>] [moves ...], go [depth N] [movetime ms]
[wtime/btime/winc/binc], stop (no-op between searches), quit.

With ``Explain`` switched on, the engine prints its English explanation as
``info string`` lines before ``bestmove``.

Usage: python uci.py
"""
from __future__ import annotations

import sys
from typing import List, Optional, TextIO

from board import Board, move_to_uci
from eval import DEFAULT_WEIGHTS, load_or_initial
from explain import explain
from search import MATE, MATE_BOUND, Limits, Searcher

ENGINE_NAME = "lossplainer 0.1"
AUTHOR = "Soham Batra"


class UCIEngine:
    """State machine handling one UCI session."""

    def __init__(self, out: TextIO = sys.stdout, weights: str = DEFAULT_WEIGHTS) -> None:
        self.out = out
        self.net = load_or_initial(weights)
        self.searcher = Searcher(self.net)
        self.board = Board()
        self.explain_enabled = False

    def send(self, text: str) -> None:
        self.out.write(text + "\n")
        self.out.flush()

    def handle(self, line: str) -> bool:
        """Process one command. Returns False when the session should end."""
        parts = line.strip().split()
        if not parts:
            return True
        cmd = parts[0]
        if cmd == "uci":
            self.send(f"id name {ENGINE_NAME}")
            self.send(f"id author {AUTHOR}")
            self.send("option name Explain type check default false")
            self.send("uciok")
        elif cmd == "isready":
            self.send("readyok")
        elif cmd == "ucinewgame":
            self.searcher = Searcher(self.net)
            self.board = Board()
        elif cmd == "setoption":
            self._setoption(parts[1:])
        elif cmd == "position":
            self._position(parts[1:])
        elif cmd == "go":
            self._go(parts[1:])
        elif cmd == "quit":
            return False
        # "stop", "debug", "register" and unknown commands are ignored.
        return True

    def _setoption(self, args: List[str]) -> None:
        if "name" in args and "value" in args:
            name = " ".join(args[args.index("name") + 1:args.index("value")])
            value = " ".join(args[args.index("value") + 1:])
            if name.lower() == "explain":
                self.explain_enabled = value.lower() == "true"

    def _position(self, args: List[str]) -> None:
        if not args:
            return
        moves: List[str] = []
        if "moves" in args:
            i = args.index("moves")
            moves = args[i + 1:]
            args = args[:i]
        if args[0] == "startpos":
            self.board = Board()
        elif args[0] == "fen":
            self.board = Board(" ".join(args[1:7]))
        for uci in moves:
            m = self.board.parse_uci(uci)
            if m is None:
                self.send(f"info string illegal move {uci}")
                break
            self.board.make(m)

    def _go(self, args: List[str]) -> None:
        depth = 4
        seconds: Optional[float] = None
        kv = {args[i]: args[i + 1] for i in range(0, len(args) - 1, 2) if args[i] != "infinite"}
        if "movetime" in kv:
            seconds = int(kv["movetime"]) / 1000.0
            depth = 64
        else:
            side_time = kv.get("wtime" if self.board.side == 1 else "btime")
            side_inc = kv.get("winc" if self.board.side == 1 else "binc", "0")
            if side_time is not None:
                seconds = max(0.05, int(side_time) / 1000.0 / 30.0 + int(side_inc) / 1000.0 * 0.5)
                depth = 64
        if "depth" in kv:
            depth = int(kv["depth"])
        elif "infinite" in args and seconds is None:
            depth = 6
        if self.explain_enabled:
            ex = explain(self.board, self.net, depth=depth, seconds=seconds, searcher=self.searcher)
            result = ex.result
            for sentence in ex.text.split("\n"):
                self.send(f"info string {sentence}")
        else:
            result = self.searcher.search(self.board, Limits(depth=depth, seconds=seconds))
        if abs(result.score) >= MATE_BOUND:
            plies = MATE - abs(result.score)
            mate = (plies + 1) // 2
            score = f"mate {mate if result.score > 0 else -mate}"
        else:
            score = f"cp {result.score}"
        self.send(f"info depth {result.depth} seldepth {result.seldepth} score {score} nodes {result.nodes} "
                  f"nps {int(result.nps)} time {int(result.seconds * 1000)} pv {result.pv_uci()}")
        if result.best_move is None:
            self.send("bestmove 0000")
        else:
            self.send(f"bestmove {move_to_uci(result.best_move)}")


def main() -> None:
    engine = UCIEngine()
    for line in sys.stdin:
        if not engine.handle(line):
            break


if __name__ == "__main__":
    main()
