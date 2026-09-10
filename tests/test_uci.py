"""UCI protocol handshake and move search."""
import io

from uci import UCIEngine


def run(commands):
    out = io.StringIO()
    engine = UCIEngine(out=out)
    for c in commands:
        if not engine.handle(c):
            break
    return out.getvalue().splitlines()


def test_uci_handshake():
    lines = run(["uci", "isready"])
    assert lines[0].startswith("id name lossplainer")
    assert "id author Soham Batra" in lines
    assert "uciok" in lines
    assert lines[-1] == "readyok"


def test_position_and_go():
    lines = run(["uci", "isready", "ucinewgame",
                 "position startpos moves e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 f3g5 d7d5 e4d5 f6d5 g5f7",
                 "go depth 2"])
    best = [l for l in lines if l.startswith("bestmove")]
    assert len(best) == 1
    assert best[0] == "bestmove e8f7"  # the only legal reply is Kxf7
    info = [l for l in lines if l.startswith("info depth")]
    assert info and " pv " in info[-1] and " nps " in info[-1]


def test_go_finds_mate_and_explains():
    lines = run(["uci", "setoption name Explain value true",
                 "position fen r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4",
                 "go depth 2", "quit"])
    assert any("score mate 1" in l for l in lines)
    assert lines[-1] == "bestmove h5f7"
    assert any(l.startswith("info string I have a forced mate in 1") for l in lines)


def test_movetime_is_honoured():
    import time
    t = time.time()
    lines = run(["position startpos", "go movetime 500"])
    assert time.time() - t < 3.0
    assert lines[-1].startswith("bestmove")
