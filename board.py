"""Chess board representation and legal move generation, written from scratch.

The board is a 10x12 mailbox: a flat list of 120 ints where the central
8x8 block holds pieces and the two-square border holds ``OFF`` so that
sliding pieces fall off the edge without bounds checks.  Squares are
indexed ``21 + file + 10 * rank`` (a1 = 21, h1 = 28, a8 = 91, h8 = 98).

Pieces are signed ints: positive for White, negative for Black, with
magnitudes ``PAWN=1 ... KING=6``.  Moves are packed ints (see ``encode``).

Positions support make/unmake with incremental Zobrist hashing, FEN
import/export, SAN import/export, and detection of checkmate, stalemate,
the fifty-move rule and threefold repetition.
"""
from __future__ import annotations

import random
from typing import Iterator, List, Optional, Tuple

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

EMPTY = 0
PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 1, 2, 3, 4, 5, 6
OFF = 99

WHITE, BLACK = 1, -1

PIECE_CHARS = ".PNBRQK"
FEN_CHARS = {"P": 1, "N": 2, "B": 3, "R": 4, "Q": 5, "K": 6,
             "p": -1, "n": -2, "b": -3, "r": -4, "q": -5, "k": -6}
CHAR_OF = {v: k for k, v in FEN_CHARS.items()}

# Castling rights bits.
CASTLE_WK, CASTLE_WQ, CASTLE_BK, CASTLE_BQ = 1, 2, 4, 8

# Move flag bits (stored in bits 17..20 of the packed move).
FLAG_CAPTURE = 1
FLAG_EP = 2
FLAG_CASTLE = 4
FLAG_DOUBLE = 8

# Mailbox geometry.
A1, H1, A8, H8 = 21, 28, 91, 98
E1, G1, C1, E8, G8, C8 = 25, 27, 23, 95, 97, 93
F1, D1, F8, D8 = 26, 24, 96, 94
B1, B8 = 22, 92

N, S = 10, -10  # one rank up / down in the mailbox
KNIGHT_DELTAS = (-21, -19, -12, -8, 8, 12, 19, 21)
KING_DELTAS = (-11, -10, -9, -1, 1, 9, 10, 11)
BISHOP_DELTAS = (-11, -9, 9, 11)
ROOK_DELTAS = (-10, -1, 1, 10)

CASTLE_MASK = [0] * 120
CASTLE_MASK[E1] = CASTLE_WK | CASTLE_WQ
CASTLE_MASK[A1] = CASTLE_WQ
CASTLE_MASK[H1] = CASTLE_WK
CASTLE_MASK[E8] = CASTLE_BK | CASTLE_BQ
CASTLE_MASK[A8] = CASTLE_BQ
CASTLE_MASK[H8] = CASTLE_BK

SQUARES = [21 + f + 10 * r for r in range(8) for f in range(8)]
FILE = [sq % 10 - 1 if sq in set(SQUARES) else -1 for sq in range(120)]
RANK = [sq // 10 - 2 if sq in set(SQUARES) else -1 for sq in range(120)]
# Chebyshev (king-move) distance between two board squares.
DISTANCE = [[max(abs(FILE[a] - FILE[b]), abs(RANK[a] - RANK[b])) if FILE[a] >= 0 and FILE[b] >= 0 else 0
             for b in range(120)] for a in range(120)]
SQUARE_NAMES = {sq: "abcdefgh"[(sq % 10) - 1] + str(sq // 10 - 1) for sq in SQUARES}
NAME_TO_SQUARE = {v: k for k, v in SQUARE_NAMES.items()}

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def file_of(sq: int) -> int:
    """0-based file (a=0) of a mailbox square."""
    return FILE[sq]


def rank_of(sq: int) -> int:
    """0-based rank (rank 1 = 0) of a mailbox square."""
    return RANK[sq]


def square_name(sq: int) -> str:
    return SQUARE_NAMES[sq]


# --------------------------------------------------------------------------
# Move packing
# --------------------------------------------------------------------------


def encode(frm: int, to: int, promo: int = 0, flags: int = 0) -> int:
    """Pack a move into an int: from(7) | to(7) | promo(3) | flags(4)."""
    return frm | (to << 7) | (promo << 14) | (flags << 17)


def move_from(m: int) -> int:
    return m & 0x7F


def move_to(m: int) -> int:
    return (m >> 7) & 0x7F


def move_promo(m: int) -> int:
    return (m >> 14) & 0x7


def move_flags(m: int) -> int:
    return (m >> 17) & 0xF


def move_to_uci(m: int) -> str:
    s = SQUARE_NAMES[move_from(m)] + SQUARE_NAMES[move_to(m)]
    p = move_promo(m)
    if p:
        s += PIECE_CHARS[p].lower()
    return s


# --------------------------------------------------------------------------
# Zobrist keys (deterministic)
# --------------------------------------------------------------------------

_rng = random.Random(20260910)
ZOBRIST_PIECE = [[_rng.getrandbits(64) for _ in range(120)] for _ in range(13)]
ZOBRIST_CASTLE = [_rng.getrandbits(64) for _ in range(16)]
ZOBRIST_EP = [_rng.getrandbits(64) for _ in range(120)]
ZOBRIST_SIDE = _rng.getrandbits(64)


def _pidx(piece: int) -> int:
    """Index 0..12 for a signed piece code (6 is EMPTY)."""
    return piece + 6


# --------------------------------------------------------------------------
# Board
# --------------------------------------------------------------------------


class Board:
    """A mutable chess position with make/unmake and legal move generation."""

    __slots__ = ("squares", "side", "castling", "ep", "halfmove", "fullmove",
                 "hash", "king_sq", "_stack", "_hash_history")

    def __init__(self, fen: str = START_FEN) -> None:
        self.squares: List[int] = [OFF] * 120
        self.side: int = WHITE
        self.castling: int = 0
        self.ep: int = 0
        self.halfmove: int = 0
        self.fullmove: int = 1
        self.hash: int = 0
        self.king_sq: List[int] = [0, 0]  # index 0 = white, 1 = black
        self._stack: List[Tuple[int, int, int, int, int, int]] = []
        self._hash_history: List[int] = []
        self.set_fen(fen)

    # ---------------------------------------------------------------- FEN

    def set_fen(self, fen: str) -> None:
        parts = fen.split()
        if len(parts) < 4:
            raise ValueError(f"bad FEN: {fen!r}")
        self.squares = [OFF] * 120
        for sq in SQUARES:
            self.squares[sq] = EMPTY
        rows = parts[0].split("/")
        if len(rows) != 8:
            raise ValueError(f"bad FEN board: {parts[0]!r}")
        for r, row in enumerate(rows):
            rank = 7 - r
            f = 0
            for ch in row:
                if ch.isdigit():
                    f += int(ch)
                else:
                    if ch not in FEN_CHARS or f > 7:
                        raise ValueError(f"bad FEN board: {parts[0]!r}")
                    self.squares[21 + f + 10 * rank] = FEN_CHARS[ch]
                    f += 1
            if f != 8:
                raise ValueError(f"bad FEN rank: {row!r}")
        self.side = WHITE if parts[1] == "w" else BLACK
        self.castling = 0
        for ch, bit in (("K", CASTLE_WK), ("Q", CASTLE_WQ), ("k", CASTLE_BK), ("q", CASTLE_BQ)):
            if ch in parts[2]:
                self.castling |= bit
        self.ep = NAME_TO_SQUARE[parts[3]] if parts[3] != "-" else 0
        self.halfmove = int(parts[4]) if len(parts) > 4 else 0
        self.fullmove = int(parts[5]) if len(parts) > 5 else 1
        for sq in SQUARES:
            if self.squares[sq] == KING:
                self.king_sq[0] = sq
            elif self.squares[sq] == -KING:
                self.king_sq[1] = sq
        self._stack = []
        self.hash = self._compute_hash()
        self._hash_history = [self.hash]

    def fen(self) -> str:
        rows = []
        for rank in range(7, -1, -1):
            row = ""
            empty = 0
            for f in range(8):
                p = self.squares[21 + f + 10 * rank]
                if p == EMPTY:
                    empty += 1
                else:
                    if empty:
                        row += str(empty)
                        empty = 0
                    row += CHAR_OF[p]
            if empty:
                row += str(empty)
            rows.append(row)
        castle = ""
        for ch, bit in (("K", CASTLE_WK), ("Q", CASTLE_WQ), ("k", CASTLE_BK), ("q", CASTLE_BQ)):
            if self.castling & bit:
                castle += ch
        ep = SQUARE_NAMES[self.ep] if self.ep else "-"
        return " ".join([
            "/".join(rows),
            "w" if self.side == WHITE else "b",
            castle or "-",
            ep,
            str(self.halfmove),
            str(self.fullmove),
        ])

    def _compute_hash(self) -> int:
        h = 0
        for sq in SQUARES:
            p = self.squares[sq]
            if p:
                h ^= ZOBRIST_PIECE[_pidx(p)][sq]
        h ^= ZOBRIST_CASTLE[self.castling]
        if self.ep:
            h ^= ZOBRIST_EP[self.ep]
        if self.side == BLACK:
            h ^= ZOBRIST_SIDE
        return h

    def copy(self) -> "Board":
        b = Board.__new__(Board)
        b.squares = self.squares[:]
        b.side = self.side
        b.castling = self.castling
        b.ep = self.ep
        b.halfmove = self.halfmove
        b.fullmove = self.fullmove
        b.hash = self.hash
        b.king_sq = self.king_sq[:]
        b._stack = []
        b._hash_history = self._hash_history[:]
        return b

    def __str__(self) -> str:
        lines = []
        for rank in range(7, -1, -1):
            row = [CHAR_OF.get(self.squares[21 + f + 10 * rank], ".") for f in range(8)]
            lines.append(f"{rank + 1}  " + " ".join(row))
        lines.append("   a b c d e f g h")
        return "\n".join(lines)

    # ------------------------------------------------------------ attacks

    def is_attacked(self, sq: int, by: int) -> bool:
        """True if ``sq`` is attacked by any piece of colour ``by``."""
        b = self.squares
        # Pawns: a white pawn on sq-9/sq-11 attacks sq.
        if by == WHITE:
            if b[sq - 9] == PAWN or b[sq - 11] == PAWN:
                return True
        else:
            if b[sq + 9] == -PAWN or b[sq + 11] == -PAWN:
                return True
        kn = KNIGHT * by
        for d in KNIGHT_DELTAS:
            if b[sq + d] == kn:
                return True
        kg = KING * by
        for d in KING_DELTAS:
            if b[sq + d] == kg:
                return True
        bi, ro, qu = BISHOP * by, ROOK * by, QUEEN * by
        for d in BISHOP_DELTAS:
            t = sq + d
            p = b[t]
            while p == EMPTY:
                t += d
                p = b[t]
            if p == bi or p == qu:
                return True
        for d in ROOK_DELTAS:
            t = sq + d
            p = b[t]
            while p == EMPTY:
                t += d
                p = b[t]
            if p == ro or p == qu:
                return True
        return False

    def in_check(self) -> bool:
        return self.is_attacked(self.king_sq[0 if self.side == WHITE else 1], -self.side)

    def pinned_squares(self) -> set:
        """Squares of side-to-move pieces pinned against their own king."""
        b = self.squares
        us = self.side
        ksq = self.king_sq[0 if us == WHITE else 1]
        pinned = set()
        for deltas, slider in ((BISHOP_DELTAS, BISHOP), (ROOK_DELTAS, ROOK)):
            for d in deltas:
                t = ksq + d
                while b[t] == EMPTY:
                    t += d
                p = b[t]
                if p == OFF or p * us <= 0:
                    continue
                own = t
                t += d
                while b[t] == EMPTY:
                    t += d
                q = b[t]
                if q != OFF and q * us < 0 and (abs(q) == slider or abs(q) == QUEEN):
                    pinned.add(own)
        return pinned

    # ------------------------------------------------------- move generation

    def pseudo_legal_moves(self, captures_only: bool = False) -> List[int]:
        """Generate pseudo-legal moves (may leave own king in check)."""
        b = self.squares
        us = self.side
        moves: List[int] = []
        push = moves.append
        if us == WHITE:
            fwd, start_rank, promo_rank = N, 3, 9  # mailbox rank rows
        else:
            fwd, start_rank, promo_rank = S, 8, 2
        for sq in SQUARES:
            p = b[sq]
            if p == EMPTY or p * us < 0:
                continue
            kind = abs(p)
            if kind == PAWN:
                row = sq // 10
                to = sq + fwd
                if b[to] == EMPTY:
                    if row + (1 if us == WHITE else -1) == promo_rank:
                        for pr in (QUEEN, ROOK, BISHOP, KNIGHT):
                            push(encode(sq, to, pr))
                    elif not captures_only:
                        push(encode(sq, to))
                        if row == start_rank and b[to + fwd] == EMPTY:
                            push(encode(sq, to + fwd, 0, FLAG_DOUBLE))
                for cd in (fwd - 1, fwd + 1):
                    to = sq + cd
                    q = b[to]
                    if q != OFF and q != EMPTY and q * us < 0:
                        if row + (1 if us == WHITE else -1) == promo_rank:
                            for pr in (QUEEN, ROOK, BISHOP, KNIGHT):
                                push(encode(sq, to, pr, FLAG_CAPTURE))
                        else:
                            push(encode(sq, to, 0, FLAG_CAPTURE))
                    elif to == self.ep and self.ep:
                        push(encode(sq, to, 0, FLAG_CAPTURE | FLAG_EP))
            elif kind == KNIGHT or kind == KING:
                for d in (KNIGHT_DELTAS if kind == KNIGHT else KING_DELTAS):
                    to = sq + d
                    q = b[to]
                    if q == EMPTY:
                        if not captures_only:
                            push(encode(sq, to))
                    elif q != OFF and q * us < 0:
                        push(encode(sq, to, 0, FLAG_CAPTURE))
            else:
                if kind == BISHOP:
                    deltas = BISHOP_DELTAS
                elif kind == ROOK:
                    deltas = ROOK_DELTAS
                else:
                    deltas = KING_DELTAS
                for d in deltas:
                    to = sq + d
                    q = b[to]
                    while q == EMPTY:
                        if not captures_only:
                            push(encode(sq, to))
                        to += d
                        q = b[to]
                    if q != OFF and q * us < 0:
                        push(encode(sq, to, 0, FLAG_CAPTURE))
        if not captures_only:
            self._castling_moves(moves)
        return moves

    def _castling_moves(self, moves: List[int]) -> None:
        b = self.squares
        if self.side == WHITE:
            if self.castling & CASTLE_WK and b[F1] == EMPTY and b[G1] == EMPTY \
                    and b[H1] == ROOK and b[E1] == KING \
                    and not self.is_attacked(E1, BLACK) and not self.is_attacked(F1, BLACK) \
                    and not self.is_attacked(G1, BLACK):
                moves.append(encode(E1, G1, 0, FLAG_CASTLE))
            if self.castling & CASTLE_WQ and b[D1] == EMPTY and b[C1] == EMPTY and b[B1] == EMPTY \
                    and b[A1] == ROOK and b[E1] == KING \
                    and not self.is_attacked(E1, BLACK) and not self.is_attacked(D1, BLACK) \
                    and not self.is_attacked(C1, BLACK):
                moves.append(encode(E1, C1, 0, FLAG_CASTLE))
        else:
            if self.castling & CASTLE_BK and b[F8] == EMPTY and b[G8] == EMPTY \
                    and b[H8] == -ROOK and b[E8] == -KING \
                    and not self.is_attacked(E8, WHITE) and not self.is_attacked(F8, WHITE) \
                    and not self.is_attacked(G8, WHITE):
                moves.append(encode(E8, G8, 0, FLAG_CASTLE))
            if self.castling & CASTLE_BQ and b[D8] == EMPTY and b[C8] == EMPTY and b[B8] == EMPTY \
                    and b[A8] == -ROOK and b[E8] == -KING \
                    and not self.is_attacked(E8, WHITE) and not self.is_attacked(D8, WHITE) \
                    and not self.is_attacked(C8, WHITE):
                moves.append(encode(E8, C8, 0, FLAG_CASTLE))

    def legal_moves(self, captures_only: bool = False) -> List[int]:
        """Generate strictly legal moves.

        Moves by unpinned non-king pieces in a position that is not check
        (and that are not en passant) cannot expose the king, so they are
        accepted without make/unmake; everything else is verified.
        """
        us = self.side
        kidx = 0 if us == WHITE else 1
        ksq = self.king_sq[kidx]
        check = self.is_attacked(ksq, -us)
        pinned = self.pinned_squares()
        out: List[int] = []
        for m in self.pseudo_legal_moves(captures_only):
            frm = m & 0x7F
            if not check and frm != ksq and frm not in pinned and not (m >> 17) & FLAG_EP:
                out.append(m)
                continue
            self.make(m)
            ok = not self.is_attacked(self.king_sq[kidx], -us)
            self.unmake()
            if ok:
                out.append(m)
        return out

    # ------------------------------------------------------------ make/unmake

    def make(self, m: int) -> None:
        """Play ``m`` on the board, pushing undo information."""
        b = self.squares
        frm = m & 0x7F
        to = (m >> 7) & 0x7F
        promo = (m >> 14) & 0x7
        flags = (m >> 17) & 0xF
        us = self.side
        piece = b[frm]
        captured = b[to]
        self._stack.append((m, captured, self.castling, self.ep, self.halfmove, self.hash))
        h = self.hash
        h ^= ZOBRIST_CASTLE[self.castling]
        if self.ep:
            h ^= ZOBRIST_EP[self.ep]

        if captured:
            h ^= ZOBRIST_PIECE[_pidx(captured)][to]
        if flags & FLAG_EP:
            cap_sq = to - N if us == WHITE else to - S
            h ^= ZOBRIST_PIECE[_pidx(b[cap_sq])][cap_sq]
            b[cap_sq] = EMPTY
        h ^= ZOBRIST_PIECE[_pidx(piece)][frm]
        b[frm] = EMPTY
        placed = (promo * us) if promo else piece
        b[to] = placed
        h ^= ZOBRIST_PIECE[_pidx(placed)][to]

        if flags & FLAG_CASTLE:
            if to == G1:
                rf, rt = H1, F1
            elif to == C1:
                rf, rt = A1, D1
            elif to == G8:
                rf, rt = H8, F8
            else:
                rf, rt = A8, D8
            rook = b[rf]
            b[rf] = EMPTY
            b[rt] = rook
            h ^= ZOBRIST_PIECE[_pidx(rook)][rf] ^ ZOBRIST_PIECE[_pidx(rook)][rt]

        if abs(piece) == KING:
            self.king_sq[0 if us == WHITE else 1] = to

        # Castling rights update: moving from or to a king/rook home square
        # removes the corresponding rights.
        c = self.castling & ~(CASTLE_MASK[frm] | CASTLE_MASK[to])
        self.castling = c
        h ^= ZOBRIST_CASTLE[c]

        # En passant target, recorded only when an enemy pawn could take
        # (so positions that differ only by an unusable ep square hash equal).
        if flags & FLAG_DOUBLE and (b[to - 1] == -piece or b[to + 1] == -piece):
            self.ep = (frm + to) // 2
            h ^= ZOBRIST_EP[self.ep]
        else:
            self.ep = 0

        if captured or abs(piece) == PAWN:
            self.halfmove = 0
        else:
            self.halfmove += 1
        if us == BLACK:
            self.fullmove += 1
        self.side = -us
        h ^= ZOBRIST_SIDE
        self.hash = h
        self._hash_history.append(h)

    def unmake(self) -> None:
        """Undo the most recent move."""
        m, captured, castling, ep, halfmove, h = self._stack.pop()
        self._hash_history.pop()
        b = self.squares
        frm = m & 0x7F
        to = (m >> 7) & 0x7F
        promo = (m >> 14) & 0x7
        flags = (m >> 17) & 0xF
        us = -self.side  # side that made the move
        piece = b[to]
        if promo:
            piece = PAWN * us
        b[frm] = piece
        b[to] = captured
        if flags & FLAG_EP:
            cap_sq = to - N if us == WHITE else to - S
            b[cap_sq] = -PAWN * us
        if flags & FLAG_CASTLE:
            if to == G1:
                rf, rt = H1, F1
            elif to == C1:
                rf, rt = A1, D1
            elif to == G8:
                rf, rt = H8, F8
            else:
                rf, rt = A8, D8
            b[rf] = b[rt]
            b[rt] = EMPTY
        if abs(piece) == KING:
            self.king_sq[0 if us == WHITE else 1] = frm
        self.castling = castling
        self.ep = ep
        self.halfmove = halfmove
        if us == BLACK:
            self.fullmove -= 1
        self.side = us
        self.hash = h

    # ----------------------------------------------------------- game state

    def is_checkmate(self) -> bool:
        return self.in_check() and not self.legal_moves()

    def is_stalemate(self) -> bool:
        return not self.in_check() and not self.legal_moves()

    def repetition_count(self) -> int:
        """Number of times the current position has occurred (including now)."""
        h = self.hash
        n = 0
        hist = self._hash_history
        # Only positions since the last irreversible move can repeat.
        start = max(0, len(hist) - 1 - self.halfmove)
        for i in range(len(hist) - 1, start - 1, -1):
            if hist[i] == h:
                n += 1
        return n

    def is_threefold(self) -> bool:
        return self.repetition_count() >= 3

    def is_fifty_moves(self) -> bool:
        return self.halfmove >= 100

    def is_insufficient_material(self) -> bool:
        pieces = [p for p in (self.squares[s] for s in SQUARES) if p and abs(p) != KING]
        if not pieces:
            return True
        if len(pieces) == 1 and abs(pieces[0]) in (KNIGHT, BISHOP):
            return True
        if all(abs(p) == BISHOP for p in pieces):
            colours = {(file_of(s) + rank_of(s)) & 1 for s in SQUARES
                       if abs(self.squares[s]) == BISHOP}
            return len(colours) == 1
        return False

    def is_draw(self) -> bool:
        return self.is_fifty_moves() or self.is_threefold() or self.is_insufficient_material()

    def result(self) -> Optional[str]:
        """'1-0', '0-1', '1/2-1/2' if the game is over, else None."""
        if not self.legal_moves():
            if self.in_check():
                return "0-1" if self.side == WHITE else "1-0"
            return "1/2-1/2"
        if self.is_draw():
            return "1/2-1/2"
        return None

    # ---------------------------------------------------------------- SAN

    def parse_uci(self, text: str) -> Optional[int]:
        text = text.strip()
        for m in self.legal_moves():
            if move_to_uci(m) == text:
                return m
        return None

    def san(self, m: int) -> str:
        """Standard algebraic notation for a legal move in this position."""
        frm, to = move_from(m), move_to(m)
        flags = move_flags(m)
        piece = abs(self.squares[frm])
        if flags & FLAG_CASTLE:
            text = "O-O" if file_of(to) == 6 else "O-O-O"
        elif piece == PAWN:
            text = ""
            if flags & FLAG_CAPTURE:
                text += SQUARE_NAMES[frm][0] + "x"
            text += SQUARE_NAMES[to]
            if move_promo(m):
                text += "=" + PIECE_CHARS[move_promo(m)]
        else:
            text = PIECE_CHARS[piece]
            others = [o for o in self.legal_moves()
                      if move_to(o) == to and move_from(o) != frm
                      and abs(self.squares[move_from(o)]) == piece]
            if others:
                same_file = any(file_of(move_from(o)) == file_of(frm) for o in others)
                same_rank = any(rank_of(move_from(o)) == rank_of(frm) for o in others)
                if not same_file:
                    text += SQUARE_NAMES[frm][0]
                elif not same_rank:
                    text += SQUARE_NAMES[frm][1]
                else:
                    text += SQUARE_NAMES[frm]
            if flags & FLAG_CAPTURE:
                text += "x"
            text += SQUARE_NAMES[to]
        self.make(m)
        if self.in_check():
            text += "#" if not self.legal_moves() else "+"
        self.unmake()
        return text

    def parse_san(self, text: str) -> Optional[int]:
        """Parse SAN (or UCI) text into a legal move, or None."""
        clean = text.strip().rstrip("+#!?").replace("0-0-0", "O-O-O").replace("0-0", "O-O")
        legal = self.legal_moves()
        for m in legal:
            if self.san(m).rstrip("+#") == clean:
                return m
        for m in legal:
            if move_to_uci(m) == clean.lower():
                return m
        return None

    def pieces(self) -> Iterator[Tuple[int, int]]:
        """Yield (square, piece) for every occupied square."""
        b = self.squares
        for sq in SQUARES:
            p = b[sq]
            if p:
                yield sq, p


def perft(board: Board, depth: int) -> int:
    """Count leaf nodes of the legal move tree to ``depth``."""
    if depth == 0:
        return 1
    moves = board.legal_moves()
    if depth == 1:
        return len(moves)
    total = 0
    for m in moves:
        board.make(m)
        total += perft(board, depth - 1)
        board.unmake()
    return total
