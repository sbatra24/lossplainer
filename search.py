"""Alpha-beta search with iterative deepening.

Features: negamax alpha-beta, transposition table with bound flags,
MVV-LVA capture ordering, two killer moves per ply, quiescence search
(captures, promotions, and all evasions when in check), check extension,
repetition and fifty-move draw detection, mate-distance scoring and a
triangular principal variation.

The evaluator is any object with ``evaluate(board) -> int`` (centipawns,
side-to-move relative).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol

from board import FLAG_CAPTURE, FLAG_EP, KING, PAWN, Board, move_to_uci

MATE = 100_000
MATE_BOUND = MATE - 1000
INF = MATE + 1
MAX_PLY = 64
QS_MAX_PLY = 10

TT_EXACT, TT_LOWER, TT_UPPER = 0, 1, 2

MVV_VALUE = {PAWN: 100, 2: 320, 3: 330, 4: 500, 5: 900, KING: 20_000}


class Evaluator(Protocol):
    def evaluate(self, board: Board) -> int: ...


class SearchAborted(Exception):
    """Raised inside the tree when a time or node limit is hit."""


@dataclass
class SearchResult:
    score: int                  # centipawns, side to move
    best_move: Optional[int]
    pv: List[int]
    depth: int
    nodes: int
    seconds: float
    seldepth: int = 0

    def pv_uci(self) -> str:
        return " ".join(move_to_uci(m) for m in self.pv)

    @property
    def nps(self) -> float:
        return self.nodes / self.seconds if self.seconds > 0 else 0.0

    def is_mate(self) -> bool:
        return abs(self.score) >= MATE_BOUND

    def mate_in(self) -> Optional[int]:
        """Moves to mate (positive: side to move mates), or None."""
        if not self.is_mate():
            return None
        plies = MATE - abs(self.score)
        moves = (plies + 1) // 2
        return moves if self.score > 0 else -moves


@dataclass
class Limits:
    depth: int = 4
    seconds: Optional[float] = None
    nodes: Optional[int] = None


@dataclass
class TTEntry:
    depth: int
    score: int
    flag: int
    move: int


@dataclass
class Searcher:
    """Reusable search object. Keep one per engine; the TT persists between calls."""

    evaluator: Evaluator
    use_tt: bool = True
    tt_exact_depth: bool = False  # strict mode: the TT is a pure cache (no grafting)
    tt: Dict[int, TTEntry] = field(default_factory=dict)
    nodes: int = 0
    seldepth: int = 0
    _killers: List[List[int]] = field(default_factory=lambda: [[0, 0] for _ in range(MAX_PLY + QS_MAX_PLY + 2)])
    _pv: List[List[int]] = field(default_factory=lambda: [[] for _ in range(MAX_PLY + QS_MAX_PLY + 3)])
    _deadline: Optional[float] = None
    _node_limit: Optional[int] = None

    # ------------------------------------------------------------ public

    def search(self, board: Board, limits: Limits = Limits()) -> SearchResult:
        """Iteratively deepen to ``limits.depth`` (or until time/nodes run out)."""
        start = time.perf_counter()
        self.nodes = 0
        self.seldepth = 0
        self._deadline = start + limits.seconds if limits.seconds else None
        self._node_limit = limits.nodes
        for k in self._killers:
            k[0] = k[1] = 0
        if len(self.tt) > 2_000_000:
            self.tt.clear()

        legal = board.legal_moves()
        if not legal:
            score = -MATE if board.in_check() else 0
            return SearchResult(score, None, [], 0, 0, time.perf_counter() - start)

        best = SearchResult(0, legal[0], [legal[0]], 0, 0, 0.0)
        for depth in range(1, limits.depth + 1):
            try:
                score = self._alphabeta(board, depth, -INF, INF, 0)
            except SearchAborted:
                break
            pv = list(self._pv[0])
            if self.use_tt and abs(score) < MATE_BOUND and len(pv) < depth:
                pv = self._extend_pv(board, pv, depth)
            best = SearchResult(score, pv[0] if pv else legal[0], pv, depth, self.nodes,
                                time.perf_counter() - start, self.seldepth)
            if abs(score) >= MATE_BOUND and MATE - abs(score) <= depth:
                break  # the mate is proven within the horizon; deeper search can't shorten it
            if self._deadline and time.perf_counter() - start > (self._deadline - start) * 0.5:
                break  # the next iteration would probably not finish
        best.nodes = self.nodes
        best.seconds = time.perf_counter() - start
        return best

    # ------------------------------------------------------------ ordering

    def _order(self, board: Board, moves: List[int], tt_move: int, ply: int) -> List[int]:
        sq = board.squares
        killers = self._killers[ply]

        def key(m: int) -> int:
            if m == tt_move:
                return 10_000_000
            score = 0
            flags = m >> 17
            if flags & FLAG_CAPTURE:
                victim = PAWN if flags & FLAG_EP else abs(sq[(m >> 7) & 0x7F])
                attacker = abs(sq[m & 0x7F])
                score = 1_000_000 + MVV_VALUE[victim] * 10 - attacker
            promo = (m >> 14) & 0x7
            if promo:
                score += 900_000 + MVV_VALUE[promo]
            if not score:
                if m == killers[0]:
                    score = 800_000
                elif m == killers[1]:
                    score = 700_000
            return score

        moves.sort(key=key, reverse=True)
        return moves

    # ------------------------------------------------------------ alpha-beta

    def _check_limits(self) -> None:
        if self.nodes & 255 == 0:
            if self._deadline is not None and time.perf_counter() > self._deadline:
                raise SearchAborted()
            if self._node_limit is not None and self.nodes > self._node_limit:
                raise SearchAborted()

    def _alphabeta(self, board: Board, depth: int, alpha: int, beta: int, ply: int) -> int:
        self._pv[ply] = []
        self.nodes += 1
        self._check_limits()

        if ply > 0:
            if board.repetition_count() >= 2 or board.halfmove >= 100:
                return 0
            # Mate-distance pruning.
            alpha = max(alpha, -MATE + ply)
            beta = min(beta, MATE - ply - 1)
            if alpha >= beta:
                return alpha

        in_check = board.in_check()
        if in_check:
            depth += 1  # check extension
        if depth <= 0 or ply >= MAX_PLY:
            return self._quiescence(board, alpha, beta, ply)

        tt_move = 0
        key = board.hash
        if self.use_tt:
            entry = self.tt.get(key)
            if entry is not None:
                tt_move = entry.move
                usable = entry.depth == depth if self.tt_exact_depth else entry.depth >= depth
                if usable and ply > 0:
                    score = self._from_tt(entry.score, ply)
                    if entry.flag == TT_EXACT:
                        return score
                    if entry.flag == TT_LOWER and score >= beta:
                        return score
                    if entry.flag == TT_UPPER and score <= alpha:
                        return score

        moves = board.legal_moves()
        if not moves:
            return -MATE + ply if in_check else 0
        self._order(board, moves, tt_move, ply)

        best_score = -INF
        best_move = 0
        orig_alpha = alpha
        for m in moves:
            board.make(m)
            score = -self._alphabeta(board, depth - 1, -beta, -alpha, ply + 1)
            board.unmake()
            if score > best_score:
                best_score = score
                best_move = m
                if score > alpha:
                    alpha = score
                    self._pv[ply] = [m] + self._pv[ply + 1]
                    if alpha >= beta:
                        if not (m >> 17) & FLAG_CAPTURE:
                            k = self._killers[ply]
                            if k[0] != m:
                                k[1] = k[0]
                                k[0] = m
                        break

        if self.use_tt:
            if best_score <= orig_alpha:
                flag = TT_UPPER
            elif best_score >= beta:
                flag = TT_LOWER
            else:
                flag = TT_EXACT
            self.tt[key] = TTEntry(depth, self._to_tt(best_score, ply), flag, best_move)
        return best_score

    def _quiescence(self, board: Board, alpha: int, beta: int, ply: int) -> int:
        self._pv[ply] = []
        self.nodes += 1
        self._check_limits()
        if ply > self.seldepth:
            self.seldepth = ply
        in_check = board.in_check()
        if in_check:
            moves = board.legal_moves()
            if not moves:
                return -MATE + ply
            if ply >= MAX_PLY + QS_MAX_PLY:
                return 0
            best = -INF
        else:
            stand_pat = self.evaluator.evaluate(board)
            if stand_pat >= beta:
                return stand_pat
            if ply >= MAX_PLY + QS_MAX_PLY:
                return stand_pat
            if stand_pat > alpha:
                alpha = stand_pat
            best = stand_pat
            moves = board.legal_moves(captures_only=True)
        self._order(board, moves, 0, ply)
        sq = board.squares
        for m in moves:
            if not in_check:
                # Delta pruning: even winning this piece cannot raise alpha.
                flags = m >> 17
                gain = MVV_VALUE[PAWN if flags & FLAG_EP else abs(sq[(m >> 7) & 0x7F])] if flags & FLAG_CAPTURE else 0
                if (m >> 14) & 0x7:
                    gain += 800
                if best + gain + 200 < alpha:
                    continue
            board.make(m)
            score = -self._quiescence(board, -beta, -alpha, ply + 1)
            board.unmake()
            if score > best:
                best = score
                if score > alpha:
                    alpha = score
                    self._pv[ply] = [m] + self._pv[ply + 1]
                    if alpha >= beta:
                        break
        return best

    def _extend_pv(self, board: Board, pv: List[int], depth: int) -> List[int]:
        """Extend a PV truncated by a TT cutoff using TT moves, then the quiescence line."""
        b = board.copy()
        out: List[int] = []
        for m in pv:
            b.make(m)
            out.append(m)
        seen = set()
        while len(out) < depth and b.hash not in seen:
            seen.add(b.hash)
            entry = self.tt.get(b.hash)
            if entry is None or entry.flag != TT_EXACT or not entry.move or entry.move not in b.legal_moves():
                break
            b.make(entry.move)
            out.append(entry.move)
            if b.repetition_count() >= 2 or b.halfmove >= 100:
                return out
        if len(out) > len(pv) and b.legal_moves():
            self._deadline = None
            self._node_limit = None
            self._quiescence(b, -INF, INF, len(out))
            out.extend(self._pv[len(out)])
        return out

    # ------------------------------------------------------------ helpers

    @staticmethod
    def _to_tt(score: int, ply: int) -> int:
        if score >= MATE_BOUND:
            return score + ply
        if score <= -MATE_BOUND:
            return score - ply
        return score

    @staticmethod
    def _from_tt(score: int, ply: int) -> int:
        if score >= MATE_BOUND:
            return score - ply
        if score <= -MATE_BOUND:
            return score + ply
        return score


def pv_leaf(board: Board, pv: List[int]) -> Board:
    """Return a copy of ``board`` after playing the principal variation."""
    b = board.copy()
    for m in pv:
        b.make(m)
    return b


def pv_san(board: Board, pv: List[int]) -> str:
    """Render a principal variation in SAN with move numbers."""
    b = board.copy()
    parts: List[str] = []
    for m in pv:
        if b.side == 1:
            parts.append(f"{b.fullmove}.")
        elif not parts:
            parts.append(f"{b.fullmove}...")
        parts.append(b.san(m))
        b.make(m)
    return " ".join(parts)


def score_text(score: int) -> str:
    """Human-readable score: '+1.30' or 'mate in 3'."""
    if abs(score) >= MATE_BOUND:
        plies = MATE - abs(score)
        n = (plies + 1) // 2
        return f"mate in {n}" if score > 0 else f"mated in {n}"
    return f"{score / 100:+.2f}"

