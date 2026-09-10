"""Search tests: mates, transposition-table consistency, limits."""
import pytest

from board import Board
from eval import EvalNet
from search import MATE, Limits, Searcher, pv_leaf

FENS = [
    "r1bq1rk1/ppp2ppp/2n5/3p4/1bP5/2N2N2/PP2PPPP/R2QKB1R w KQ - 0 8",
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
    "2r3k1/pp3ppp/4p3/3pP3/3P4/2P2N2/P4PPP/2R3K1 b - - 0 20",
    "8/8/4k3/3p4/3P1K2/8/8/8 w - - 0 1",
]


def test_finds_mate_in_one():
    net = EvalNet.initial()
    res = Searcher(net).search(Board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4"),
                               Limits(depth=3))
    assert res.mate_in() == 1
    assert res.pv_uci() == "h5f7"


def test_finds_mate_in_two():
    net = EvalNet.initial()
    res = Searcher(net).search(Board("6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1"), Limits(depth=4))
    assert res.mate_in() == 1
    # Classic: 1. Qd8+ Bxd8 2. Re8#
    res = Searcher(net).search(Board("r1b2k1r/ppp1bppp/8/1B1Q4/5q2/2P5/PPP2PPP/R3R1K1 w - - 1 0"), Limits(depth=4))
    assert res.mate_in() == 2
    assert res.score == MATE - 3
    assert res.pv_uci() == "d5d8 e7d8 e1e8"


@pytest.mark.parametrize("fen", FENS)
def test_tt_strict_mode_matches_search_without_tt(fen):
    """With the TT used as a pure cache (exact-depth entries only) the fixed-depth
    score must equal a search with no transposition table at all."""
    net = EvalNet.initial()
    without = Searcher(net, use_tt=False).search(Board(fen), Limits(depth=4))
    strict = Searcher(net, use_tt=True, tt_exact_depth=True).search(Board(fen), Limits(depth=4))
    assert without.depth == strict.depth == 4
    assert without.score == strict.score
    assert strict.nodes <= without.nodes


@pytest.mark.parametrize("fen", FENS[:2])
def test_pv_leaf_static_eval_equals_score(fen):
    net = EvalNet.initial()
    b = Board(fen)
    res = Searcher(net).search(b, Limits(depth=4))
    leaf = pv_leaf(b, res.pv)
    static = net.evaluate(leaf) * (1 if leaf.side == b.side else -1)
    assert static == res.score


def test_time_limit_is_respected():
    net = EvalNet.initial()
    res = Searcher(net).search(Board(FENS[1]), Limits(depth=20, seconds=1.0))
    assert res.seconds < 2.5
    assert res.best_move is not None
    assert res.nps > 0


def test_no_legal_moves():
    net = EvalNet.initial()
    res = Searcher(net).search(Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1"), Limits(depth=3))
    assert res.best_move is None and res.score == 0
