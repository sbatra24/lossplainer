"""Turn the evaluation network's verdict into English.

Pipeline for ``explain(board)``:

1. search the position; take the principal variation and its leaf;
2. attribute the network's score at the leaf to the named input features
   with Integrated Gradients (hand-rolled, with a completeness check) and,
   separately, with group ablation (zero one feature group, re-evaluate);
3. render sentences from templates keyed by chess concept, filled with the
   actual attribution numbers and the squares/pieces behind each feature.

``explain_discrepancy(board)`` is the "what did I get wrong" mode: it
compares the static evaluation of the root with the deeper search value and
attributes the difference to feature changes along the principal variation,
naming the move in the line where each change happens.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from board import Board
from eval import EvalNet
from features import (FEATURE_INDEX, FEATURES, GROUPS, PIECE_VALUE, concept_of,
                      extract, swap_perspective)
from search import MATE_BOUND, Limits, SearchResult, Searcher, pv_san, score_text

# --------------------------------------------------------------------------
# Attribution
# --------------------------------------------------------------------------


@dataclass
class Attribution:
    """Per-feature attributions plus the completeness bookkeeping."""

    values: np.ndarray          # one entry per feature, in pawns
    baseline_output: float
    output: float
    steps: int

    @property
    def completeness_error(self) -> float:
        return abs(float(self.values.sum()) - (self.output - self.baseline_output))


def integrated_gradients(net: EvalNet, x: np.ndarray, baseline: Optional[np.ndarray] = None,
                         steps: int = 64, tol: float = 1e-5, max_steps: int = 4096) -> Attribution:
    """Integrated Gradients of ``net`` at ``x`` from ``baseline`` (default: all zeros).

    Uses the midpoint Riemann sum and doubles the step count until the sum of
    attributions matches ``net(x) - net(baseline)`` to within ``tol``.
    """
    if baseline is None:
        baseline = np.zeros_like(x)
    diff = x - baseline
    fx = float(net.forward(x))
    fb = float(net.forward(baseline))
    while True:
        alphas = (np.arange(steps) + 0.5) / steps
        path = baseline + alphas[:, None] * diff[None, :]
        grads = net.input_gradient(path)              # (steps, features)
        attr = diff * grads.mean(axis=0)
        att = Attribution(attr, fb, fx, steps)
        if att.completeness_error <= tol or steps >= max_steps:
            return att
        steps *= 2


def group_ablation(net: EvalNet, x: np.ndarray) -> Dict[str, float]:
    """Score change from zeroing each feature group: f(x) - f(x with group zeroed)."""
    fx = float(net.forward(x))
    out: Dict[str, float] = {}
    for group in GROUPS:
        if group == "global":
            continue
        xa = x.copy()
        for i, f in enumerate(FEATURES):
            if f.group == group:
                xa[i] = 0.0
        out[group] = fx - float(net.forward(xa))
    return out


# --------------------------------------------------------------------------
# English rendering
# --------------------------------------------------------------------------

_PIECE_WORD = {"P": "pawn", "N": "knight", "B": "bishop", "R": "rook", "Q": "queen", "K": "king"}
_PLURAL = {"pawn": "pawns", "knight": "knights", "bishop": "bishops", "rook": "rooks", "queen": "queens"}


def _join(items: Sequence[str]) -> str:
    items = list(items)
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def _piece_phrase(code: str) -> str:
    """'Nc3' -> 'knight on c3'."""
    return f"{_PIECE_WORD[code[0]]} on {code[1:]}"


def _files_phrase(files: Sequence[str]) -> str:
    """['f-file', 'g-file'] -> 'the open f- and g-files'."""
    letters = [f[0] for f in files]
    if len(letters) == 1:
        return f"the {letters[0]}-file"
    return "the " + ", ".join(f"{l}-" for l in letters[:-1]) + f" and {letters[-1]}-files"


def concept_phrase(concept: str, who: str, evidence: Sequence[str], value: float) -> str:
    """Noun phrase for a feature, from the engine's point of view ('my'/'your')."""
    my = "my" if who == "mine" else "your"
    ev = list(evidence)
    n = int(round(abs(value)))

    def squares(noun: str) -> str:
        if ev:
            return f"{my} {noun if len(ev) == 1 else _PLURAL.get(noun, noun + 's')} on {_join(ev)}"
        return f"{my} {noun if n == 1 else _PLURAL.get(noun, noun + 's')}"

    def pieces_list(default: str) -> str:
        if ev:
            return f"{my} {_join(_piece_phrase(p) for p in ev)}"
        return f"{my} {default}"

    table = {
        "passed_pawns": lambda: squares("passed pawn"),
        "passed_advancement": lambda: f"how far {squares('passed pawn')} {'has' if len(ev) == 1 else 'have'} advanced",
        "best_passer_rank": lambda: f"the rank of {my} most advanced passed pawn" + (f" ({ev[0]})" if len(ev) == 1 else ""),
        "passed_blocked": lambda: f"the blockade on {squares('passed pawn')}",
        "king_pawn_shield": lambda: f"the pawn shelter in front of {my} king",
        "king_open_files": lambda: f"{_files_phrase(ev) if ev else 'the files'} around {my} king being open",
        "king_zone_attackers": lambda: f"{'your' if who == 'mine' else 'my'} {_join(_piece_phrase(p) for p in ev) if ev else 'pieces'} aiming at {my} king",
        "king_zone_attacks": lambda: f"the number of attacks on the squares around {my} king",
        "king_castled": lambda: f"{my} king being castled",
        "castling_rights": lambda: f"{my} remaining castling rights",
        "pawn_storm": lambda: f"{my} pawns marching at {'your' if who == 'mine' else 'my'} king",
        "doubled_pawns": lambda: f"{my} doubled pawns on {_files_phrase(ev) if ev else 'one file'}",
        "isolated_pawns": lambda: squares("isolated pawn"),
        "backward_pawns": lambda: squares("backward pawn"),
        "connected_pawns": lambda: f"{my} connected pawns",
        "pawn_islands": lambda: (f"{my} pawns forming a single group" if n == 1
                                 else f"{my} pawns being split into {n} islands"),
        "pawns_advanced": lambda: f"{my} pawns across the middle of the board",
        "bishop_pair": lambda: f"{my} bishop pair",
        "rook_open_file": lambda: f"{my} rook on the open {_join(ev)}" if ev else f"{my} rook on an open file",
        "rook_semi_open_file": lambda: f"{my} rook on the half-open {_join(ev)}" if ev else f"{my} rook on a half-open file",
        "rook_on_seventh": lambda: f"{my} rook on the seventh rank" + (f" ({_join(ev)})" if ev else ""),
        "rook_behind_passer": lambda: f"{my} rook standing behind {my} passed pawn",
        "knight_outpost": lambda: f"{my} knight outpost on {_join(ev)}" if ev else f"{my} knight outpost",
        "knights_on_rim": lambda: f"{my} knight on the edge of the board ({_join(ev)})" if ev else f"{my} knight on the rim",
        "bad_bishop_pawns": lambda: f"{my} pawns sitting on the same colour as {my} bishop",
        "minors_undeveloped": lambda: f"{my} undeveloped minor piece{'s' if n != 1 else ''}",
        "connected_rooks": lambda: f"{my} connected rooks",
        "hanging_pieces": lambda: pieces_list("hanging piece") + (" hanging" if ev else ""),
        "attacked_by_lower": lambda: pieces_list("piece") + " being attacked by something cheaper",
        "pinned_pieces": lambda: pieces_list("piece") + " being pinned",
        "pawn_threats": lambda: f"{my} pawn{'s' if n != 1 else ''} attacking {'your' if who == 'mine' else 'my'} {_join(_piece_phrase(p) for p in ev) if ev else 'pieces'}",
        "center_control": lambda: f"{my} control of the central squares",
        "center_pawns": lambda: f"{my} pawn{'s' if n != 1 else ''} in the centre",
        "space": lambda: f"the space behind {my} pawns",
        "king_centralization": lambda: f"{my} king being centralised for the endgame",
        "king_pawn_distance": lambda: f"how far {my} king is from {my} pawns",
        "knight_mobility": lambda: f"how much room {my} knights have",
        "bishop_mobility": lambda: f"how much room {my} bishops have",
        "rook_mobility": lambda: f"how much room {my} rooks have",
        "queen_mobility": lambda: f"how much room {my} queen has",
        "pawn_pst": lambda: f"the squares {my} pawns stand on",
        "knight_pst": lambda: f"the squares {my} knights stand on",
        "bishop_pst": lambda: f"the squares {my} bishops stand on",
        "rook_pst": lambda: f"the squares {my} rooks stand on",
        "queen_pst": lambda: f"where {my} queen stands",
        "king_pst": lambda: f"where {my} king stands",
        "pawns": lambda: f"{my} pawn count",
        "knights": lambda: f"{my} knight count",
        "bishops": lambda: f"{my} bishop count",
        "rooks": lambda: f"{my} rook count",
        "queens": lambda: f"{my} queen count",
        "material_total": lambda: f"{my} total material",
        "material_balance": lambda: "the material balance",
        "phase": lambda: "the stage of the game",
        "bias": lambda: "the network's constant offset",
    }
    return table[concept]()


def material_summary(leaf: Board, side: int) -> Tuple[str, float]:
    """('up a knight for two pawns', +1.2) for ``side`` in ``leaf``."""
    mine = {k: 0 for k in "PNBRQ"}
    theirs = {k: 0 for k in "PNBRQ"}
    for _, p in leaf.pieces():
        kind = abs(p)
        if kind == 6:
            continue
        letter = "PNBRQ"[kind - 1]
        (mine if (p > 0) == (side > 0) else theirs)[letter] += 1
    plus: List[str] = []
    minus: List[str] = []
    balance = 0.0
    for letter, name in (("Q", "queen"), ("R", "rook"), ("B", "bishop"), ("N", "knight"), ("P", "pawn")):
        d = mine[letter] - theirs[letter]
        balance += d * PIECE_VALUE["PNBRQ".index(letter) + 1]
        if d > 0:
            plus.append(f"{'a' if d == 1 else d} {name if d == 1 else _PLURAL[name]}")
        elif d < 0:
            minus.append(f"{'a' if d == -1 else -d} {name if d == -1 else _PLURAL[name]}")
    if not plus and not minus:
        return "material is level", 0.0
    if plus and not minus:
        return "I'm up " + _join(plus), balance
    if minus and not plus:
        return "I'm down " + _join(minus), balance
    if balance >= 0:
        return f"I have {_join(plus)} for {_join(minus)}", balance
    return f"you have {_join(minus)} for {_join(plus)}", balance


def _fmt(x: float) -> str:
    return f"{x:+.2f}"


def _cap(text: str) -> str:
    """Capitalise only the first character."""
    return text[:1].upper() + text[1:]


# --------------------------------------------------------------------------
# Explanation objects
# --------------------------------------------------------------------------


@dataclass
class FeatureContribution:
    name: str
    concept: str
    who: str
    group: str
    value: float            # attribution in pawns, engine's (root side) perspective
    feature_value: float    # raw feature value at the leaf
    evidence: List[str] = field(default_factory=list)

    def phrase(self) -> str:
        return concept_phrase(self.concept, self.who, self.evidence, self.feature_value)


@dataclass
class Explanation:
    fen: str
    result: SearchResult
    leaf_fen: str
    pv_text: str
    score_pawns: float                 # root-side perspective, pawns
    contributions: List[FeatureContribution]
    group_totals: Dict[str, float]
    ablation: Dict[str, float]
    completeness_error: float
    ig_steps: int
    residual: float                    # search score minus leaf static eval (0 unless mate/draw/TT effects)
    text: str


def _contributions(attr: np.ndarray, x_root_persp: np.ndarray, evidence: Dict[str, List[str]],
                   flip: bool) -> List[FeatureContribution]:
    """Map an attribution vector to named contributions in the root side's words."""
    out: List[FeatureContribution] = []
    for i, f in enumerate(FEATURES):
        concept, who = concept_of(f.name)
        if flip and who in ("mine", "theirs"):
            who = "theirs" if who == "mine" else "mine"
        name = f"{concept}_{who}" if who != "global" else concept
        out.append(FeatureContribution(name, concept, who, f.group, float(attr[i]),
                                       float(x_root_persp[FEATURE_INDEX[name]]),
                                       list(evidence.get(f.name, []))))
    return out


def _leaf_attribution(net: EvalNet, root: Board, leaf: Board
                      ) -> Tuple[Attribution, List[FeatureContribution], np.ndarray]:
    """IG at the leaf, converted to the root side's perspective."""
    x_leaf, evidence = extract(leaf, with_evidence=True)
    att = integrated_gradients(net, x_leaf)
    flip = leaf.side != root.side
    attr = -att.values if flip else att.values
    x_root_persp = swap_perspective(x_leaf) if flip else x_leaf
    contribs = _contributions(attr, x_root_persp, evidence or {}, flip)
    if flip:
        att = Attribution(attr, -att.baseline_output, -att.output, att.steps)
    return att, contribs, x_root_persp


def _verdict(score: float, result: SearchResult) -> str:
    if result.best_move is None:
        return "The game is over: I'm checkmated." if result.score < 0 else "The game is over: stalemate."
    mate = result.mate_in()
    if mate is not None:
        return f"I have a forced mate in {mate}." if mate > 0 else f"I'm getting mated in {-mate}."
    if abs(score) < 0.15:
        return f"This looks about equal ({_fmt(score)})."
    word = "winning" if score > 0 else "losing"
    return f"I'm {word} by about {abs(score):.1f} pawn{'s' if abs(score) >= 1.5 else ''}."


def render_explanation(score: float, result: SearchResult, board: Board, leaf: Board,
                       contribs: List[FeatureContribution], group_totals: Dict[str, float],
                       top_k: int = 3, min_abs: float = 0.12) -> str:
    """Compose the English explanation from attribution numbers."""
    lines: List[str] = [_verdict(score, result)]
    pv = pv_san(board, result.pv)
    mat_text, mat_balance = material_summary(leaf, board.side)
    if result.is_mate():
        lines.append(f"The line is {pv}. No need to weigh features when the king is the issue.")
        return "\n".join(lines)
    if result.pv:
        lines.append(f"I'm expecting {pv}, after which {mat_text}.")
    else:
        lines.append(f"Right now {mat_text}.")

    # Concept-level aggregation: the same concept for both sides becomes one
    # item whose phrase follows the dominant side.  Material counts are
    # folded into a single "material" item because the sentence above
    # already states the imbalance in chess terms.
    by_concept: Dict[str, List[FeatureContribution]] = {}
    for c in contribs:
        key = "material" if c.group == "material" else c.concept
        by_concept.setdefault(key, []).append(c)
    items: List[Tuple[str, float]] = []
    for key, cs in by_concept.items():
        total = sum(c.value for c in cs)
        if key == "bias" or abs(total) < min_abs:
            continue
        if key == "material":
            phrase = "the material balance" if mat_balance == 0 else f"the material ({mat_text})"
        else:
            dominant = max(cs, key=lambda c: abs(c.value))
            phrase = dominant.phrase()
        items.append((phrase, total))

    sign = 1.0 if score >= 0 else -1.0
    same = sorted([it for it in items if it[1] * sign > 0], key=lambda it: -abs(it[1]))
    against = sorted([it for it in items if it[1] * sign < 0], key=lambda it: -abs(it[1]))
    if abs(score) < 0.15:
        # Balanced: name the largest factor on each side.
        plus = sorted([it for it in items if it[1] > 0], key=lambda it: -it[1])
        minus = sorted([it for it in items if it[1] < 0], key=lambda it: it[1])
        if plus and minus:
            lines.append(f"What I have going for me: {plus[0][0]} ({_fmt(plus[0][1])}). "
                         f"What you have: {minus[0][0]} ({_fmt(minus[0][1])}). They roughly cancel.")
        elif not plus and not minus:
            lines.append("Nothing in the position stands out to me; every factor is small.")
        return "\n".join(lines)

    if same:
        lines.append(f"The biggest reason is {same[0][0]} ({_fmt(same[0][1])}).")
        rest = same[1:top_k]
        if rest:
            lines.append(_cap(_join([f"{p} ({_fmt(v)})" for p, v in rest]))
                         + (" also count" if len(rest) > 1 else " also counts")
                         + (" for me." if sign > 0 else " against me."))
    if against:
        p, v = against[0]
        words = "in my favour" if v > 0 else "against me"
        lines.append(f"{_cap(p)} works {words} ({_fmt(v)}), but that's worth less than "
                     f"{same[0][0] if same else 'the rest'}.")
    themed = sorted(((g, t) for g, t in group_totals.items() if abs(t) >= 0.05 and g != "global"),
                    key=lambda gt: -abs(gt[1]))
    if themed:
        lines.append("By theme: " + ", ".join(f"{g.replace('_', ' ')} {_fmt(t)}" for g, t in themed) + ".")
    return "\n".join(lines)


def explain(board: Board, net: EvalNet, depth: int = 4, seconds: Optional[float] = None,
            searcher: Optional[Searcher] = None) -> Explanation:
    """Search ``board`` and explain the resulting evaluation in English."""
    searcher = searcher or Searcher(net)
    result = searcher.search(board, Limits(depth=depth, seconds=seconds))
    leaf = board.copy()
    for m in result.pv:
        leaf.make(m)
    att, contribs, x_root = _leaf_attribution(net, board, leaf)
    score = result.score / 100.0
    if abs(result.score) >= MATE_BOUND:
        score = float(np.sign(result.score)) * 99.0
    residual = score - att.output
    group_totals: Dict[str, float] = {}
    for c in contribs:
        group_totals[c.group] = group_totals.get(c.group, 0.0) + c.value
    x_leaf, _ = extract(leaf)
    flip = leaf.side != board.side
    ablation = {g: (-v if flip else v) for g, v in group_ablation(net, x_leaf).items()}
    text = render_explanation(score, result, board, leaf, contribs, group_totals)
    return Explanation(
        fen=board.fen(), result=result, leaf_fen=leaf.fen(), pv_text=pv_san(board, result.pv),
        score_pawns=score, contributions=sorted(contribs, key=lambda c: -abs(c.value)),
        group_totals=group_totals, ablation=ablation, completeness_error=att.completeness_error,
        ig_steps=att.steps, residual=residual, text=text)


# --------------------------------------------------------------------------
# "What did I get wrong" mode
# --------------------------------------------------------------------------


@dataclass
class Discrepancy:
    fen: str
    static_score: float        # net(root), pawns, root side
    search_score: float        # search value, pawns, root side
    pv_text: str
    contributions: List[FeatureContribution]   # attribution of (leaf eval - root eval)
    change_ply: Dict[str, Tuple[int, str]]      # feature -> (ply, SAN move) where it changed most
    residual: float            # search score minus leaf static eval
    completeness_error: float
    text: str


def explain_discrepancy(board: Board, net: EvalNet, depth: int = 4, seconds: Optional[float] = None,
                        searcher: Optional[Searcher] = None, top_k: int = 4) -> Discrepancy:
    """Explain why the search disagrees with the network's first impression."""
    searcher = searcher or Searcher(net)
    result = searcher.search(board, Limits(depth=depth, seconds=seconds))
    x_root, ev_root = extract(board, with_evidence=True)
    static = float(net.forward(x_root))
    search_score = result.score / 100.0 if abs(result.score) < MATE_BOUND else float(np.sign(result.score)) * 99.0

    # Features of every position along the PV, expressed from the root side's view.
    b = board.copy()
    path_vecs: List[np.ndarray] = [x_root]
    sans: List[str] = []
    for m in result.pv:
        sans.append(b.san(m))
        b.make(m)
        x, _ = extract(b)
        path_vecs.append(swap_perspective(x) if b.side != board.side else x)
    leaf = b
    _, ev_leaf = extract(leaf, with_evidence=True)
    x_leaf_root = path_vecs[-1]
    residual = search_score - float(net.forward(x_leaf_root))

    att = integrated_gradients(net, x_leaf_root, baseline=x_root)
    flip = leaf.side != board.side
    evidence_leaf: Dict[str, List[str]] = {}
    for name, texts in (ev_leaf or {}).items():
        concept, who = concept_of(name)
        if flip and who != "global":
            who = "theirs" if who == "mine" else "mine"
        evidence_leaf[f"{concept}_{who}" if who != "global" else concept] = texts
    evidence_root = ev_root or {}
    contribs: List[FeatureContribution] = []
    deltas: Dict[str, float] = {}
    for i, f in enumerate(FEATURES):
        delta = float(x_leaf_root[i] - x_root[i])
        deltas[f.name] = delta
        # A feature that shrinks or vanishes is best described by what it was at the root.
        evidence = evidence_root.get(f.name, []) if delta < 0 else evidence_leaf.get(f.name, [])
        shown_value = float(x_root[i]) if delta < 0 else float(x_leaf_root[i])
        contribs.append(FeatureContribution(f.name, *concept_of(f.name), f.group, float(att.values[i]),
                                            shown_value, evidence))
    contribs.sort(key=lambda c: -abs(c.value))

    # Where along the line does each feature change the most?
    change_ply: Dict[str, Tuple[int, str]] = {}
    for c in contribs:
        i = FEATURE_INDEX[c.name]
        best_ply, best_delta = 0, 0.0
        for ply in range(1, len(path_vecs)):
            d = path_vecs[ply][i] - path_vecs[ply - 1][i]
            if abs(d) > abs(best_delta):
                best_ply, best_delta = ply, d
        if best_ply:
            change_ply[c.name] = (best_ply, sans[best_ply - 1])

    text = _render_discrepancy(board, leaf, static, search_score, result, contribs, change_ply,
                               deltas, residual, top_k)
    return Discrepancy(board.fen(), static, search_score, pv_san(board, result.pv), contribs,
                       change_ply, residual, att.completeness_error, text)


def _move_label(ply: int) -> str:
    """'my move 2 of the line' for a ply index 1.. along the PV."""
    n = (ply + 1) // 2
    mover = "my" if ply % 2 == 1 else "your"
    return f"{mover} move {n} of the line"


def _render_discrepancy(board: Board, leaf: Board, static: float, search_score: float,
                        result: SearchResult, contribs: List[FeatureContribution],
                        change_ply: Dict[str, Tuple[int, str]], deltas: Dict[str, float],
                        residual: float, top_k: int) -> str:
    delta = search_score - static
    lines = [f"At a glance I thought this position was {_fmt(static)}. "
             f"After searching {result.depth} plies ahead I make it {score_text(result.score)} "
             f"(a swing of {_fmt(delta)})."]
    line = pv_san(board, result.pv)
    if result.is_mate():
        lines.append(f"The static evaluation cannot see a mate; the line is {line}.")
        return "\n".join(lines)
    if abs(delta) < 0.1:
        lines.append(f"My first impression was about right; the line {line} doesn't change much.")
        return "\n".join(lines)
    lines.append(f"The line I expect is {line}.")

    # Material features are summarised as one item in chess terms.
    mat_root, _ = material_summary(board, board.side)
    mat_leaf, _ = material_summary(leaf, board.side)
    # (phrase, attribution, where it changes, feature delta or None for the material item, group)
    items: List[Tuple[str, float, Optional[Tuple[int, str]], Optional[float], str]] = []
    continuous = {"placement", "mobility", "center", "endgame"}  # graded features, no "appears/disappears"
    mat_total = 0.0
    mat_where: Optional[Tuple[int, str]] = None
    mat_best = 0.0
    for c in contribs:
        if c.group == "material":
            mat_total += c.value
            if abs(c.value) > mat_best and c.name in change_ply:
                mat_best, mat_where = abs(c.value), change_ply[c.name]
        elif abs(c.value) >= 0.1 and c.concept != "bias":
            items.append((c.phrase(), c.value, change_ply.get(c.name), deltas[c.name], c.group))
    if abs(mat_total) >= 0.1:
        items.append((f"material (at first {mat_root}; after the line {mat_leaf})", mat_total, mat_where, None, "material"))
    items.sort(key=lambda it: -abs(it[1]))

    for phrase, value, where, delta, group in items[:top_k]:
        if delta is None:
            sentence = f"The biggest part is {phrase}, worth {_fmt(value)}" if value == items[0][1] \
                else f"{_cap(phrase)} accounts for {_fmt(value)}"
        elif group in continuous:
            sentence = (f"{_cap(phrase)} turns against me over the line ({_fmt(value)})" if value < 0
                        else f"{_cap(phrase)} improves for me over the line ({_fmt(value)})")
        elif value < 0 and delta > 0:
            sentence = f"My first look didn't see {phrase} coming; that costs me {_fmt(value)} once the line plays out"
        elif value < 0 and delta < 0:
            sentence = f"My first look was counting on {phrase}, which goes away in the line ({_fmt(value)})"
        elif value > 0 and delta > 0:
            sentence = f"My first look missed {phrase}, which appears in the line and is worth {_fmt(value)}"
        elif value > 0 and delta < 0:
            sentence = f"My first look was too worried about {phrase}; it disappears in the line, worth {_fmt(value)} to me"
        else:
            sentence = f"{_cap(phrase)} reads differently in the final position ({_fmt(value)})"
        if where:
            sentence += f"; it changes after {where[1]} ({_move_label(where[0])})."
        else:
            sentence += "."
        lines.append(sentence)
    if abs(residual) >= 0.1:
        lines.append(f"Another {_fmt(residual)} comes from the search itself (a draw score or a "
                     f"capture sequence past the end of the line).")
    return "\n".join(lines)


def contribution_table(contribs: List[FeatureContribution], k: int = 10) -> str:
    """Plain-text table of the top-k concepts, netting the 'mine' and 'theirs' halves.

    With an all-zero baseline the two halves of a balanced feature (my rooks,
    your rooks) carry large opposite attributions; showing them side by side
    makes the net effect readable.
    """
    by_concept: Dict[str, Dict[str, FeatureContribution]] = {}
    for c in contribs:
        by_concept.setdefault(c.concept, {})[c.who] = c
    rows = []
    for concept, parts in by_concept.items():
        mine = parts.get("mine")
        theirs = parts.get("theirs")
        glob = parts.get("global")
        net = sum(c.value for c in parts.values())
        evidence = []
        for c in (mine, theirs):
            if c is not None and c.evidence:
                evidence.append(("mine: " if c is mine else "theirs: ") + ", ".join(c.evidence[:3]))
        rows.append((concept, net, mine.value if mine else (glob.value if glob else 0.0),
                     theirs.value if theirs else 0.0, "; ".join(evidence)))
    rows.sort(key=lambda r: -abs(r[1]))
    out = [f"{'concept':<22} {'net':>8} {'mine':>8} {'theirs':>8}   evidence"]
    for concept, net, m, t, ev in rows[:k]:
        out.append(f"{concept:<22} {net:+8.3f} {m:+8.3f} {t:+8.3f}   {ev}")
    return "\n".join(out)
