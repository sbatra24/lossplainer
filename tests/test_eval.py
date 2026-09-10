"""Evaluation network: initialisation, antisymmetry and gradients."""
import numpy as np
import pytest

from board import Board
from eval import EvalNet, MaterialEval
from features import (FEATURE_NAMES, NUM_FEATURES, extract, material_pst_eval,
                      swap_perspective)

FENS = [
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
    "r1bq1rk1/ppp2ppp/2n5/3p4/1bP5/2N2N2/PP2PPPP/R2QKB1R w KQ - 0 8",
    "8/8/4k3/3p4/3P1K2/8/8/8 b - - 0 1",
]


def perturbed_net(seed: int = 1) -> EvalNet:
    net = EvalNet.initial()
    rng = np.random.default_rng(seed)
    net.W2 = rng.normal(0.0, 0.3, size=net.W2.shape)
    net.b1 = rng.normal(0.0, 0.1, size=net.b1.shape)
    return net


def test_feature_count_and_names_unique():
    assert 100 <= NUM_FEATURES <= 300
    assert len(set(FEATURE_NAMES)) == NUM_FEATURES


@pytest.mark.parametrize("fen", FENS)
def test_initial_net_equals_material_plus_pst(fen):
    x, _ = extract(Board(fen))
    assert EvalNet.initial()(x) == pytest.approx(material_pst_eval(x), abs=1e-9)


def test_start_position_is_zero_and_symmetric():
    x, _ = extract(Board())
    assert EvalNet.initial()(x) == pytest.approx(0.0, abs=1e-9)
    assert np.allclose(swap_perspective(x), x)


@pytest.mark.parametrize("fen", FENS)
def test_antisymmetry(fen):
    net = perturbed_net()
    b = Board(fen)
    x, _ = extract(b)
    flipped = b.copy()
    flipped.side = -flipped.side
    x2, _ = extract(flipped)
    assert np.allclose(x2, swap_perspective(x))
    assert net(x2) == pytest.approx(-net(x), abs=1e-9)


def test_input_gradient_matches_finite_differences():
    net = perturbed_net()
    x, _ = extract(Board(FENS[0]))
    analytic = net.input_gradient(x)
    eps = 1e-6
    for i in range(0, NUM_FEATURES, 7):
        e = np.zeros(NUM_FEATURES)
        e[i] = eps
        numeric = (net(x + e) - net(x - e)) / (2 * eps)
        assert analytic[i] == pytest.approx(numeric, abs=1e-6)


def test_parameter_gradients_match_finite_differences():
    net = perturbed_net()
    X = np.stack([extract(Board(f))[0] for f in FENS])
    y = np.array([0.3, -0.5, 0.1])
    _, grads = net.loss_and_grads(X, y)
    eps = 1e-6
    rng = np.random.default_rng(0)
    for name in ("w_lin", "W1", "b1", "W2"):
        flat = getattr(net, name).reshape(-1)
        for i in rng.integers(0, flat.size, 4):
            old = flat[i]
            flat[i] = old + eps
            lp, _ = net.loss_and_grads(X, y)
            flat[i] = old - eps
            lm, _ = net.loss_and_grads(X, y)
            flat[i] = old
            assert grads[name].reshape(-1)[i] == pytest.approx((lp - lm) / (2 * eps), abs=1e-6)


def test_save_load_round_trip(tmp_path):
    net = perturbed_net()
    path = tmp_path / "w.npz"
    net.save(str(path))
    loaded = EvalNet.load(str(path))
    x, _ = extract(Board(FENS[1]))
    assert loaded(x) == pytest.approx(net(x))


def test_material_eval_sign():
    b = Board("4k3/8/8/8/8/8/8/4KQ2 w - - 0 1")
    assert MaterialEval().evaluate(b) == 900
    b.side = -1
    assert MaterialEval().evaluate(b) == -900
