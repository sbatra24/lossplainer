"""Move generation, FEN, SAN and draw detection tests."""
import random

import pytest

from board import START_FEN, Board, move_to_uci, perft

KIWIPETE = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"


@pytest.mark.parametrize("depth,expected", [(1, 20), (2, 400), (3, 8902), (4, 197281)])
def test_perft_start_position(depth, expected):
    assert perft(Board(), depth) == expected


@pytest.mark.parametrize("depth,expected", [(1, 48), (2, 2039), (3, 97862)])
def test_perft_kiwipete(depth, expected):
    assert perft(Board(KIWIPETE), depth) == expected


@pytest.mark.parametrize("fen,depth,expected", [
    ("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", 4, 43238),
    ("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1", 3, 9467),
    ("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8", 3, 62379),
])
def test_perft_other_standard_positions(fen, depth, expected):
    assert perft(Board(fen), depth) == expected


@pytest.mark.parametrize("fen", [
    START_FEN,
    KIWIPETE,
    "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
    "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
])
def test_fen_round_trip(fen):
    assert Board(fen).fen() == fen


def test_make_unmake_restores_everything():
    b = Board(KIWIPETE)
    before = (b.fen(), b.hash, list(b.king_sq))
    rng = random.Random(0)
    for _ in range(30):
        moves = b.legal_moves()
        if not moves:
            break
        b.make(rng.choice(moves))
    while b._stack:
        b.unmake()
    assert (b.fen(), b.hash, list(b.king_sq)) == before


def test_incremental_hash_matches_recomputed():
    b = Board(KIWIPETE)
    rng = random.Random(1)
    for _ in range(40):
        moves = b.legal_moves()
        if not moves:
            break
        b.make(rng.choice(moves))
        assert b.hash == b._compute_hash()


def test_checkmate_and_stalemate():
    assert Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3").is_checkmate()
    assert Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1").is_stalemate()
    assert Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1").result() == "1/2-1/2"
    assert Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3").result() == "0-1"


def test_threefold_repetition_and_fifty_moves():
    b = Board("8/8/8/8/8/4k3/8/4K2R w - - 0 1")
    for _ in range(2):
        for uci in ("h1h2", "e3d3", "h2h1", "d3e3"):
            b.make(b.parse_uci(uci))
            assert not b.is_threefold() or uci == "d3e3"
    assert b.is_threefold()
    assert b.result() == "1/2-1/2"
    assert Board("8/8/8/8/8/4k3/8/4K2R w - - 100 80").is_fifty_moves()
    assert not Board("8/8/8/8/8/4k3/8/4K2R w - - 99 80").is_fifty_moves()


def test_san_and_parsing():
    b = Board()
    for san in ("e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "O-O"):
        m = b.parse_san(san)
        assert m is not None, san
        assert b.san(m) == san
        b.make(m)
    # Disambiguation and promotion.
    b = Board("4k3/1P6/8/8/8/8/8/R4RK1 w - - 0 1")
    assert b.san(b.parse_uci("b7b8q")) == "b8=Q+"
    assert b.san(b.parse_uci("a1d1")) == "Rad1"
    assert b.parse_san("Rfd1") == b.parse_uci("f1d1")


def test_en_passant_and_castling_moves_exist():
    b = Board("rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3")
    assert "e5f6" in {move_to_uci(m) for m in b.legal_moves()}
    b = Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    ucis = {move_to_uci(m) for m in b.legal_moves()}
    assert {"e1g1", "e1c1"} <= ucis
    b.make(b.parse_uci("e1g1"))
    assert b.fen().startswith("r3k2r/8/8/8/8/8/8/R4RK1 b kq")


def test_cross_check_against_python_chess():
    chess = pytest.importorskip("chess")
    rng = random.Random(2024)
    positions = 0
    for _ in range(40):
        ref = chess.Board()
        mine = Board()
        for _ply in range(rng.randint(5, 90)):
            if ref.is_game_over():
                break
            ours = sorted(move_to_uci(m) for m in mine.legal_moves())
            theirs = sorted(m.uci() for m in ref.legal_moves)
            assert ours == theirs, ref.fen()
            assert mine.fen() == ref.fen(en_passant="xfen")
            assert mine.in_check() == ref.is_check()
            positions += 1
            uci = rng.choice(theirs)
            ref.push_uci(uci)
            mine.make(mine.parse_uci(uci))
            assert mine.is_threefold() == ref.is_repetition(3)
    assert positions > 300
