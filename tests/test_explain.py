"""Integrated gradients completeness and explanation fidelity."""
import numpy as np
import pytest

from board import Board
from eval import EvalNet
from explain import (concept_phrase, explain, explain_discrepancy, group_ablation,
                     integrated_gradients)
from features import FEATURES, concept_of, extract

FENS = [
    "r1bq1rk1/ppp2ppp/2n5/3p4/1bP5/2N2N2/PP2PPPP/R2QKB1R w KQ - 0 8",
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
    "8/5pk1/6p1/3P4/8/6P1/5PK1/8 b - - 0 1",
]


def perturbed_net(seed: int = 3) -> EvalNet:
    net = EvalNet.initial()
    rng = np.random.default_rng(seed)
    net.W2 = rng.normal(0.0, 0.4, size=net.W2.shape)
    net.b1 = rng.normal(0.0, 0.2, size=net.b1.shape)
    return net


@pytest.mark.parametrize("fen", FENS)
def test_integrated_gradients_completeness(fen):
    net = perturbed_net()
    x, _ = extract(Board(fen))
    att = integrated_gradients(net, x)
    assert att.completeness_error < 1e-4
    assert float(att.values.sum()) == pytest.approx(net(x) - net(np.zeros_like(x)), abs=1e-4)


def test_integrated_gradients_linear_net_is_exact():
    net = EvalNet.initial()  # W2 = 0: the net is linear, so IG must equal w * x exactly
    x, _ = extract(Board(FENS[1]))
    att = integrated_gradients(net, x)
    expected = x * net.input_gradient(x)
    assert np.allclose(att.values, expected, atol=1e-12)
    assert att.steps == 64


def test_completeness_with_nonzero_baseline():
    net = perturbed_net()
    x0, _ = extract(Board(FENS[0]))
    x1, _ = extract(Board(FENS[1]))
    att = integrated_gradients(net, x1, baseline=x0)
    assert att.completeness_error < 1e-4


def test_ablation_groups_cover_every_feature():
    net = perturbed_net()
    x, _ = extract(Board(FENS[1]))
    abl = group_ablation(net, x)
    assert set(abl) == {f.group for f in FEATURES} - {"global"}


def test_every_concept_has_a_phrase():
    piece_concepts = {"hanging_pieces", "attacked_by_lower", "pinned_pieces", "pawn_threats", "king_zone_attackers"}
    file_concepts = {"king_open_files", "doubled_pawns", "rook_open_file", "rook_semi_open_file"}
    for f in FEATURES:
        concept, who = concept_of(f.name)
        who = who if who != "global" else "mine"
        evidence = (["Nc3", "Bb5"] if concept in piece_concepts
                    else ["f-file", "g-file"] if concept in file_concepts else ["d5", "e6"])
        for ev in (evidence, evidence[:1], []):
            text = concept_phrase(concept, who, ev, 2.0)
            assert isinstance(text, str) and text


@pytest.mark.parametrize("fen", FENS)
def test_explanation_mentions_top_attributions(fen):
    """The sentences must be built from the biggest attributed concepts."""
    net = perturbed_net()
    ex = explain(Board(fen), net, depth=2)
    assert ex.completeness_error < 1e-4
    assert abs(ex.residual) < 0.02  # the leaf's static eval is the search score
    text = ex.text
    # Group totals in the "By theme" line must match the attribution sums.
    for group, total in ex.group_totals.items():
        if abs(total) >= 0.05 and group != "global":
            assert f"{group.replace('_', ' ')} {total:+.2f}" in text
    # The largest non-material concept of the winning side's sign must be named.
    sign = 1.0 if ex.score_pawns >= 0 else -1.0
    by_concept = {}
    for c in ex.contributions:
        key = "material" if c.group == "material" else c.concept
        by_concept.setdefault(key, []).append(c)
    ranked = sorted(((k, sum(c.value for c in cs), cs) for k, cs in by_concept.items()),
                    key=lambda t: -abs(t[1]))
    same = [t for t in ranked if t[1] * sign > 0 and abs(t[1]) >= 0.12 and t[0] != "bias"]
    if abs(ex.score_pawns) >= 0.15 and same:
        key, total, cs = same[0]
        dominant = max(cs, key=lambda c: abs(c.value))
        phrase = "the material" if key == "material" else dominant.phrase()
        assert phrase in text
        assert f"({total:+.2f})" in text


def test_discrepancy_mode_reports_swing_and_move():
    net = perturbed_net()
    d = explain_discrepancy(Board("r1bq1rk1/ppp2ppp/2n5/3p4/1bP5/2N2N2/PP2PPPP/R2QKB1R w KQ - 0 8"),
                            net, depth=3)
    assert d.completeness_error < 1e-4
    assert f"{d.static_score:+.2f}" in d.text
    assert f"a swing of {d.search_score - d.static_score:+.2f}" in d.text
    if abs(d.search_score - d.static_score) >= 0.1:
        assert "of the line" in d.text
