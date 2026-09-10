"""Named, human-readable evaluation features.

Every input to the evaluation network is registered here with a name, a
group and a one-line description, so that attributions computed on the
network can be mapped back to chess concepts.  Features are computed from
the point of view of the side to move: ``*_mine`` features describe the
side to move, ``*_theirs`` describe the opponent.

``extract(board)`` returns the feature vector (float32, in natural units:
counts, pawn-valued sums, fractions) plus optional "evidence", a mapping
from feature name to the squares or pieces responsible for it, which the
explainer uses to say *which* passed pawn or *which* open file it means.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from board import (BISHOP, BISHOP_DELTAS, BLACK, DISTANCE, EMPTY, FILE, KING,
                   KING_DELTAS, KNIGHT, KNIGHT_DELTAS, OFF, PAWN, QUEEN, RANK,
                   ROOK, ROOK_DELTAS, SQUARES, WHITE, Board, file_of, rank_of,
                   square_name)

# --------------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Feature:
    """One named input to the evaluation network."""

    name: str
    group: str
    description: str
    init_weight: float = 0.0  # weight in the hand-tuned linear initialisation


# (concept, group, description, init weight for "mine"; "theirs" gets the negation)
_SIDE_CONCEPTS: List[Tuple[str, str, str, float]] = [
    # material
    ("pawns", "material", "number of pawns", 1.0),
    ("knights", "material", "number of knights", 3.2),
    ("bishops", "material", "number of bishops", 3.3),
    ("rooks", "material", "number of rooks", 5.0),
    ("queens", "material", "number of queens", 9.0),
    ("material_total", "material", "total non-king material in pawns", 0.0),
    # piece-square tables (sum over pieces of a classical PST, in pawns)
    ("pawn_pst", "placement", "pawn piece-square score", 1.0),
    ("knight_pst", "placement", "knight piece-square score", 1.0),
    ("bishop_pst", "placement", "bishop piece-square score", 1.0),
    ("rook_pst", "placement", "rook piece-square score", 1.0),
    ("queen_pst", "placement", "queen piece-square score", 1.0),
    ("king_pst", "placement", "king piece-square score, blended by game phase", 1.0),
    # mobility
    ("knight_mobility", "mobility", "squares reachable by knights", 0.0),
    ("bishop_mobility", "mobility", "squares reachable by bishops", 0.0),
    ("rook_mobility", "mobility", "squares reachable by rooks", 0.0),
    ("queen_mobility", "mobility", "squares reachable by the queen", 0.0),
    # king safety
    ("king_pawn_shield", "king_safety", "own pawns directly sheltering the king", 0.0),
    ("king_open_files", "king_safety", "files next to the king with no own pawn", 0.0),
    ("king_zone_attackers", "king_safety", "enemy pieces attacking squares around the king", 0.0),
    ("king_zone_attacks", "king_safety", "enemy attacks on squares around the king", 0.0),
    ("king_castled", "king_safety", "king has reached a castled position", 0.0),
    ("castling_rights", "king_safety", "castling options still available", 0.0),
    ("pawn_storm", "king_safety", "own pawns advanced toward the enemy king", 0.0),
    # pawn structure
    ("doubled_pawns", "pawn_structure", "pawns doubled on a file", 0.0),
    ("isolated_pawns", "pawn_structure", "pawns with no friendly pawn on adjacent files", 0.0),
    ("backward_pawns", "pawn_structure", "pawns behind all neighbours and unable to advance safely", 0.0),
    ("connected_pawns", "pawn_structure", "pawns defended by another pawn", 0.0),
    ("pawn_islands", "pawn_structure", "groups of pawns on adjacent files", 0.0),
    ("passed_pawns", "passed_pawns", "pawns with no enemy pawn ahead on the same or adjacent files", 0.0),
    ("passed_advancement", "passed_pawns", "sum of passed-pawn progress, 0 (home) to 5 (seventh rank)", 0.0),
    ("best_passer_rank", "passed_pawns", "progress of the most advanced passed pawn", 0.0),
    ("passed_blocked", "passed_pawns", "passed pawns with a piece directly in front", 0.0),
    ("pawns_advanced", "pawn_structure", "pawns across the middle of the board", 0.0),
    # pieces
    ("bishop_pair", "pieces", "owns both bishops", 0.0),
    ("rook_open_file", "pieces", "rooks on files with no pawns", 0.0),
    ("rook_semi_open_file", "pieces", "rooks on files with only enemy pawns", 0.0),
    ("rook_on_seventh", "pieces", "rooks on the seventh rank", 0.0),
    ("rook_behind_passer", "pieces", "rooks behind own passed pawns", 0.0),
    ("knight_outpost", "pieces", "knights on protected advanced squares enemy pawns cannot reach", 0.0),
    ("knights_on_rim", "pieces", "knights on the edge of the board", 0.0),
    ("bad_bishop_pawns", "pieces", "own pawns on the same colour as own bishops", 0.0),
    ("minors_undeveloped", "development", "knights and bishops still on their home squares", 0.0),
    ("connected_rooks", "pieces", "rooks defending each other", 0.0),
    # threats
    ("hanging_pieces", "threats", "pieces attacked and not defended", 0.0),
    ("attacked_by_lower", "threats", "pieces attacked by a cheaper enemy piece", 0.0),
    ("pinned_pieces", "threats", "pieces pinned against the king", 0.0),
    ("pawn_threats", "threats", "enemy pieces attacked by own pawns", 0.0),
    # centre and space
    ("center_control", "center", "attacks on d4, e4, d5 and e5", 0.0),
    ("center_pawns", "center", "own pawns on d4, e4, d5 or e5", 0.0),
    ("space", "center", "safe squares in own half on the c to f files", 0.0),
    # endgame king
    ("king_centralization", "endgame", "king closeness to the centre, weighted by endgame-ness", 0.0),
    ("king_pawn_distance", "endgame", "king distance to own pawns, weighted by endgame-ness", 0.0),
]

_GLOBAL_FEATURES: List[Feature] = [
    Feature("phase", "global", "game phase from non-pawn material, 1 = opening, 0 = bare endgame"),
    Feature("material_balance", "material", "material of side to move minus opponent, in pawns"),
    Feature("bias", "global", "constant 1"),
]


def _build_registry() -> List[Feature]:
    feats: List[Feature] = []
    for who, sign in (("mine", 1.0), ("theirs", -1.0)):
        owner = "my" if who == "mine" else "opponent's"
        for concept, group, desc, w in _SIDE_CONCEPTS:
            feats.append(Feature(f"{concept}_{who}", group, f"{owner} {desc}", sign * w))
    feats.extend(_GLOBAL_FEATURES)
    return feats


FEATURES: List[Feature] = _build_registry()
FEATURE_NAMES: List[str] = [f.name for f in FEATURES]
FEATURE_INDEX: Dict[str, int] = {f.name: i for i, f in enumerate(FEATURES)}
NUM_FEATURES: int = len(FEATURES)
GROUPS: List[str] = sorted({f.group for f in FEATURES})
INIT_WEIGHTS = np.array([f.init_weight for f in FEATURES], dtype=np.float64)

_N_SIDE = len(_SIDE_CONCEPTS)
_CONCEPT_INDEX = {c[0]: i for i, c in enumerate(_SIDE_CONCEPTS)}

# Swapping perspective: exchange the "mine" and "theirs" blocks and negate
# the material balance.  ``swap_perspective(x)`` is the feature vector the
# opponent would see for the same position.
PERSPECTIVE_PERM = np.array(
    list(range(_N_SIDE, 2 * _N_SIDE)) + list(range(_N_SIDE)) + list(range(2 * _N_SIDE, NUM_FEATURES)))
PERSPECTIVE_SIGN = np.ones(NUM_FEATURES)
PERSPECTIVE_SIGN[FEATURE_INDEX["material_balance"]] = -1.0


def swap_perspective(vec: np.ndarray) -> np.ndarray:
    """Re-express feature vector(s) from the other side's point of view."""
    return PERSPECTIVE_SIGN * vec[..., PERSPECTIVE_PERM]


def concept_of(name: str) -> Tuple[str, str]:
    """Split 'passed_pawns_mine' into ('passed_pawns', 'mine')."""
    for suffix in ("_mine", "_theirs"):
        if name.endswith(suffix):
            return name[: -len(suffix)], suffix[1:]
    return name, "global"


# --------------------------------------------------------------------------
# Piece-square tables (centipawns, from White's view, rank 8 listed first)
# --------------------------------------------------------------------------

_PST_RAW = {
    PAWN: [
        0, 0, 0, 0, 0, 0, 0, 0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5, 5, 10, 25, 25, 10, 5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, -5, -10, 0, 0, -10, -5, 5,
        5, 10, 10, -20, -20, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0],
    KNIGHT: [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50],
    BISHOP: [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20],
    ROOK: [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0],
    QUEEN: [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0, -10,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20],
    "KING_MG": [
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, 0, 0, 0, 0, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20],
    "KING_EG": [
        -50, -40, -30, -20, -20, -30, -40, -50,
        -30, -20, -10, 0, 0, -10, -20, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -30, 0, 0, 0, 0, -30, -30,
        -50, -30, -30, -30, -30, -30, -30, -50],
}


def _to_mailbox(table: List[int], colour: int) -> List[float]:
    """Map a rank-8-first 64-table to a 120-mailbox for the given colour (pawns)."""
    out = [0.0] * 120
    for sq in SQUARES:
        f, r = file_of(sq), rank_of(sq)
        row = (7 - r) if colour == WHITE else r
        out[sq] = table[row * 8 + f] / 100.0
    return out


PST: Dict[Tuple[object, int], List[float]] = {}
for _key, _tab in _PST_RAW.items():
    for _col in (WHITE, BLACK):
        PST[(_key, _col)] = _to_mailbox(_tab, _col)

PIECE_VALUE = {PAWN: 1.0, KNIGHT: 3.2, BISHOP: 3.3, ROOK: 5.0, QUEEN: 9.0, KING: 0.0}
_MAX_NONPAWN = 2 * (2 * 3.2 + 2 * 3.3 + 2 * 5.0 + 9.0)
CENTER = [54, 55, 64, 65]  # d4 e4 d5 e5
_HOME_MINORS = {WHITE: (22, 23, 26, 27), BLACK: (92, 93, 96, 97)}
_KING_AREA = {WHITE: (21, 22, 23, 27, 28), BLACK: (91, 92, 93, 97, 98)}


# --------------------------------------------------------------------------
# Attack generation helpers
# --------------------------------------------------------------------------


def piece_attacks(b: List[int], sq: int, piece: int) -> List[int]:
    """Squares attacked by ``piece`` standing on ``sq`` (own pieces included)."""
    kind = abs(piece)
    out: List[int] = []
    if kind == PAWN:
        d = 10 if piece > 0 else -10
        for t in (sq + d - 1, sq + d + 1):
            if b[t] != OFF:
                out.append(t)
        return out
    if kind == KNIGHT or kind == KING:
        for d in (KNIGHT_DELTAS if kind == KNIGHT else KING_DELTAS):
            if b[sq + d] != OFF:
                out.append(sq + d)
        return out
    deltas = BISHOP_DELTAS if kind == BISHOP else ROOK_DELTAS if kind == ROOK else KING_DELTAS
    for d in deltas:
        t = sq + d
        while b[t] == EMPTY:
            out.append(t)
            t += d
        if b[t] != OFF:
            out.append(t)
    return out


def _pinned_for(board: Board, us: int) -> List[int]:
    """Squares of ``us`` pieces pinned to their king (works for either side)."""
    b = board.squares
    ksq = board.king_sq[0 if us == WHITE else 1]
    pinned: List[int] = []
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
                pinned.append(own)
    return pinned


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------

_PIECE_LETTER = "PNBRQK"
_FILE_NAMES = "abcdefgh"
_PST_NAME = {PAWN: "pawn_pst", KNIGHT: "knight_pst", BISHOP: "bishop_pst",
             ROOK: "rook_pst", QUEEN: "queen_pst"}
_MOB_NAME = {KNIGHT: "knight_mobility", BISHOP: "bishop_mobility",
             ROOK: "rook_mobility", QUEEN: "queen_mobility"}
_CI = _CONCEPT_INDEX  # short alias used heavily below
_ZONE_DELTAS = KING_DELTAS + (0,)


def extract(board: Board, with_evidence: bool = False
            ) -> Tuple[np.ndarray, Optional[Dict[str, List[str]]]]:
    """Compute the feature vector for ``board`` from the side to move's view.

    Returns ``(vector, evidence)``; ``evidence`` is None unless requested.
    Evidence maps a feature name to short strings such as ``"d5"`` or
    ``"Nc3"`` naming the squares or pieces that produced the feature.
    """
    b = board.squares
    us = board.side
    ev: Optional[Dict[str, List[str]]] = {} if with_evidence else None

    # Pass 1: pieces, attack maps, pawn files, material.
    pieces: Dict[int, List[Tuple[int, int]]] = {WHITE: [], BLACK: []}
    attacks: Dict[int, Dict[int, List[int]]] = {WHITE: {}, BLACK: {}}  # target -> attackers
    piece_att: Dict[int, List[int]] = {}
    pawn_files: Dict[int, List[List[int]]] = {WHITE: [[] for _ in range(8)], BLACK: [[] for _ in range(8)]}
    nonpawn = {WHITE: 0.0, BLACK: 0.0}
    for sq in SQUARES:
        p = b[sq]
        if not p:
            continue
        col = WHITE if p > 0 else BLACK
        pieces[col].append((sq, p))
        kind = p if p > 0 else -p
        if kind == PAWN:
            pawn_files[col][FILE[sq]].append(RANK[sq])
        elif kind != KING:
            nonpawn[col] += PIECE_VALUE[kind]
        att = piece_attacks(b, sq, p)
        piece_att[sq] = att
        amap = attacks[col]
        for t in att:
            lst = amap.get(t)
            if lst is None:
                amap[t] = [sq]
            else:
                lst.append(sq)

    phase = min(1.0, (nonpawn[WHITE] + nonpawn[BLACK]) / _MAX_NONPAWN)
    endgame = 1.0 - phase

    side_vecs: Dict[int, List[float]] = {}
    side_ev: Dict[int, Dict[str, List[str]]] = {WHITE: {}, BLACK: {}}
    material = {WHITE: 0.0, BLACK: 0.0}

    for col in (WHITE, BLACK):
        them = -col
        v = [0.0] * _N_SIDE
        e = side_ev[col]
        my_att = attacks[col]
        their_att = attacks[them]
        my_pawn_files = pawn_files[col]
        their_pawn_files = pawn_files[them]
        ksq = board.king_sq[0 if col == WHITE else 1]
        eksq = board.king_sq[0 if them == WHITE else 1]
        ekf = FILE[eksq]
        fwd = 1 if col == WHITE else -1          # rank direction
        up = 10 * fwd                            # mailbox delta for one step forward
        my_pawn = PAWN * col
        their_pawn = -my_pawn
        counts = {PAWN: 0, KNIGHT: 0, BISHOP: 0, ROOK: 0, QUEEN: 0}
        bishops_sq: List[int] = []
        rooks_sq: List[int] = []
        passers: List[int] = []
        best_passer = 0
        pst_king = PST[("KING_MG", col)]
        pst_king_eg = PST[("KING_EG", col)]

        def note(name: str, text: str) -> None:
            if ev is not None:
                e.setdefault(name, []).append(text)

        for sq, p in pieces[col]:
            kind = p if p > 0 else -p
            f = FILE[sq]
            r = RANK[sq]
            rr = r if col == WHITE else 7 - r  # rank relative to own side, 0..7
            if kind == KING:
                v[_CI["king_pst"]] += phase * pst_king[sq] + endgame * pst_king_eg[sq]
                continue
            counts[kind] += 1
            material[col] += PIECE_VALUE[kind]
            v[_CI[_PST_NAME[kind]]] += PST[(kind, col)][sq]
            # Threats against this piece.
            attackers = their_att.get(sq)
            if attackers:
                if sq not in my_att:
                    v[_CI["hanging_pieces"]] += 1
                    note("hanging_pieces", _PIECE_LETTER[kind - 1] + square_name(sq))
                if kind != PAWN:
                    cheapest = min(PIECE_VALUE[abs(b[a])] for a in attackers)
                    if cheapest < PIECE_VALUE[kind]:
                        v[_CI["attacked_by_lower"]] += 1
                        note("attacked_by_lower", _PIECE_LETTER[kind - 1] + square_name(sq))
            if kind == PAWN:
                passed = True
                for ff in (f - 1, f, f + 1):
                    if 0 <= ff < 8:
                        for orank in their_pawn_files[ff]:
                            if (orank - r) * fwd > 0:
                                passed = False
                                break
                    if not passed:
                        break
                if passed:
                    passers.append(sq)
                    v[_CI["passed_pawns"]] += 1
                    v[_CI["passed_advancement"]] += rr - 1
                    if rr - 1 > v[_CI["best_passer_rank"]]:
                        v[_CI["best_passer_rank"]] = rr - 1
                        best_passer = sq
                    note("passed_pawns", square_name(sq))
                    note("passed_advancement", square_name(sq))
                    if b[sq + up] != EMPTY:
                        v[_CI["passed_blocked"]] += 1
                        note("passed_blocked", square_name(sq))
                if rr >= 4:
                    v[_CI["pawns_advanced"]] += 1
                has_neighbour = (f > 0 and my_pawn_files[f - 1]) or (f < 7 and my_pawn_files[f + 1])
                if not has_neighbour:
                    v[_CI["isolated_pawns"]] += 1
                    note("isolated_pawns", square_name(sq))
                elif b[sq - up - 1] == my_pawn or b[sq - up + 1] == my_pawn:
                    v[_CI["connected_pawns"]] += 1
                else:
                    behind_all = True
                    for ff in (f - 1, f + 1):
                        if 0 <= ff < 8:
                            for orank in my_pawn_files[ff]:
                                if (orank - r) * fwd <= 0:
                                    behind_all = False
                    stop = sq + up
                    if behind_all and (b[stop + up - 1] == their_pawn or b[stop + up + 1] == their_pawn):
                        v[_CI["backward_pawns"]] += 1
                        note("backward_pawns", square_name(sq))
                if rr >= 4 and -1 <= ekf - f <= 1:
                    v[_CI["pawn_storm"]] += 1
                if sq in CENTER:
                    v[_CI["center_pawns"]] += 1
            else:
                mob = 0
                for t in piece_att[sq]:
                    if b[t] * col <= 0:
                        mob += 1
                v[_CI[_MOB_NAME[kind]]] += mob
                if kind == KNIGHT:
                    if f == 0 or f == 7:
                        v[_CI["knights_on_rim"]] += 1
                        note("knights_on_rim", square_name(sq))
                    if 3 <= rr <= 5 and (b[sq - up - 1] == my_pawn or b[sq - up + 1] == my_pawn):
                        safe = True
                        for ff in (f - 1, f + 1):
                            if 0 <= ff < 8:
                                for orank in their_pawn_files[ff]:
                                    if (orank - r) * fwd > 0:
                                        safe = False
                        if safe:
                            v[_CI["knight_outpost"]] += 1
                            note("knight_outpost", square_name(sq))
                    if sq in _HOME_MINORS[col]:
                        v[_CI["minors_undeveloped"]] += 1
                elif kind == BISHOP:
                    bishops_sq.append(sq)
                    if sq in _HOME_MINORS[col]:
                        v[_CI["minors_undeveloped"]] += 1
                elif kind == ROOK:
                    rooks_sq.append(sq)
                    if not my_pawn_files[f]:
                        if not their_pawn_files[f]:
                            v[_CI["rook_open_file"]] += 1
                            note("rook_open_file", _FILE_NAMES[f] + "-file")
                        else:
                            v[_CI["rook_semi_open_file"]] += 1
                            note("rook_semi_open_file", _FILE_NAMES[f] + "-file")
                    if rr == 6:
                        v[_CI["rook_on_seventh"]] += 1
                        note("rook_on_seventh", square_name(sq))

        if best_passer:
            note("best_passer_rank", square_name(best_passer))
        # Bishop pair and bishops hemmed in by own pawns.
        if len(bishops_sq) >= 2:
            colours = {(FILE[s] + RANK[s]) & 1 for s in bishops_sq}
            if len(colours) == 2:
                v[_CI["bishop_pair"]] = 1.0
        for bsq in bishops_sq:
            bc = (FILE[bsq] + RANK[bsq]) & 1
            same = 0
            for ff in range(8):
                for orank in my_pawn_files[ff]:
                    if (ff + orank) & 1 == bc:
                        same += 1
            v[_CI["bad_bishop_pawns"]] += same
        # Rooks behind passers, connected rooks.
        for rsq in rooks_sq:
            for psq in passers:
                if FILE[rsq] == FILE[psq] and (RANK[psq] - RANK[rsq]) * fwd > 0:
                    v[_CI["rook_behind_passer"]] += 1
                    note("rook_behind_passer", square_name(rsq))
        if len(rooks_sq) == 2 and rooks_sq[1] in piece_att[rooks_sq[0]]:
            v[_CI["connected_rooks"]] = 1.0
        # File-level pawn structure.
        islands = 0
        prev = False
        for ff in range(8):
            n = len(my_pawn_files[ff])
            if n > 1:
                v[_CI["doubled_pawns"]] += n - 1
                note("doubled_pawns", _FILE_NAMES[ff] + "-file")
            if n and not prev:
                islands += 1
            prev = n > 0
        v[_CI["pawn_islands"]] = islands
        # King safety.
        kf = FILE[ksq]
        krr = RANK[ksq] if col == WHITE else 7 - RANK[ksq]
        shield = 0
        for dx in (-1, 0, 1):
            if b[ksq + up + dx] == my_pawn:
                shield += 1
            if b[ksq + 2 * up + dx] == my_pawn:
                shield += 1
        v[_CI["king_pawn_shield"]] = shield
        for ff in (kf - 1, kf, kf + 1):
            if 0 <= ff < 8 and not my_pawn_files[ff]:
                v[_CI["king_open_files"]] += 1
                note("king_open_files", _FILE_NAMES[ff] + "-file")
        zone_attackers: set = set()
        zone_attacks = 0
        for d in _ZONE_DELTAS:
            a = their_att.get(ksq + d)
            if a:
                zone_attacks += len(a)
                zone_attackers.update(a)
        v[_CI["king_zone_attackers"]] = len(zone_attackers)
        v[_CI["king_zone_attacks"]] = zone_attacks
        if ev is not None:
            for a in sorted(zone_attackers):
                note("king_zone_attackers", _PIECE_LETTER[abs(b[a]) - 1] + square_name(a))
        rights = (board.castling >> (0 if col == WHITE else 2)) & 3
        v[_CI["castling_rights"]] = (rights & 1) + (rights >> 1)
        if rights == 0 and krr == 0 and ksq in _KING_AREA[col]:
            v[_CI["king_castled"]] = 1.0
        # Centre control and space.
        cc = 0
        for c in CENTER:
            a = my_att.get(c)
            if a:
                cc += len(a)
        v[_CI["center_control"]] = cc
        space = 0
        for ff in range(2, 6):
            for srr in (1, 2, 3):
                sq = 21 + ff + 10 * (srr if col == WHITE else 7 - srr)
                if b[sq] * col >= 0 and b[sq + up - 1] != their_pawn and b[sq + up + 1] != their_pawn:
                    space += 1
        v[_CI["space"]] = space
        # Enemy pieces attacked by own pawns.
        pt = 0
        for sq, p in pieces[them]:
            kind = p if p > 0 else -p
            if kind != PAWN and kind != KING and (b[sq - up - 1] == my_pawn or b[sq - up + 1] == my_pawn):
                pt += 1
                note("pawn_threats", _PIECE_LETTER[kind - 1] + square_name(sq))
        v[_CI["pawn_threats"]] = pt
        # Pins.
        pins = _pinned_for(board, col)
        v[_CI["pinned_pieces"]] = len(pins)
        for s in pins:
            note("pinned_pieces", _PIECE_LETTER[abs(b[s]) - 1] + square_name(s))
        # Endgame king terms.
        if endgame > 0.0:
            dist_row = DISTANCE[ksq]
            kdist_center = min(dist_row[c] for c in CENTER)
            v[_CI["king_centralization"]] = endgame * (3 - kdist_center)
            total = 0
            npawns = 0
            for ff in range(8):
                for orank in my_pawn_files[ff]:
                    total += dist_row[21 + ff + 10 * orank]
                    npawns += 1
            if npawns:
                v[_CI["king_pawn_distance"]] = endgame * total / npawns
        # Material counts.
        v[_CI["pawns"]] = counts[PAWN]
        v[_CI["knights"]] = counts[KNIGHT]
        v[_CI["bishops"]] = counts[BISHOP]
        v[_CI["rooks"]] = counts[ROOK]
        v[_CI["queens"]] = counts[QUEEN]
        v[_CI["material_total"]] = material[col]
        side_vecs[col] = v

    vec = np.empty(NUM_FEATURES, dtype=np.float64)
    vec[:_N_SIDE] = side_vecs[us]
    vec[_N_SIDE:2 * _N_SIDE] = side_vecs[-us]
    g = 2 * _N_SIDE
    vec[g] = phase
    vec[g + 1] = material[us] - material[-us]
    vec[g + 2] = 1.0
    if ev is not None:
        for concept, texts in side_ev[us].items():
            ev[concept + "_mine"] = texts
        for concept, texts in side_ev[-us].items():
            ev[concept + "_theirs"] = texts
    return vec, ev


def material_pst_eval(vec: np.ndarray) -> float:
    """The hand-tuned linear evaluation (material + PST) the net starts from."""
    return float(vec @ INIT_WEIGHTS)
