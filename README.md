# lossplainer

A chess engine I wrote from scratch in Python that tells you, in English, why it thinks it's winning or losing. The evaluation is a small neural network over 107 features that all have names (my passed pawns, your king's open files, my bishop pair). After every search the engine runs Integrated Gradients on its own network, reads off which features carried the score, and turns the numbers into sentences.

Here is the engine looking at the Kiwipete test position, playing White, after a depth 4 search. This is the verbatim output from `outputs/examples.md`.

> I'm winning by about 0.3 pawn.
>
> I'm expecting 1. dxe6 Qxe6 2. Bxa6 hxg2, after which I have a bishop for a pawn.
>
> The biggest reason is the material (I have a bishop for a pawn) (+1.72).
>
> My bishop pair (+0.63) and my rook on h1 and knight on c3 being attacked by something cheaper (+0.28) also count for me.
>
> The rank of your most advanced passed pawn (g2) works against me (-0.77), but that's worth less than the material (I have a bishop for a pawn).
>
> By theme: material +1.72, passed pawns -1.22, pawn structure -0.53, center +0.23, placement +0.22, king safety -0.12, threats +0.12, pieces -0.08, mobility -0.08.

And here it is on the same position in the second mode, where it compares its first static impression with what the search found and explains the gap:

> At a glance I thought this position was +1.25. After searching 4 plies ahead I make it +0.35 (a swing of -0.90).
>
> The line I expect is 1. dxe6 Qxe6 2. Bxa6 hxg2.
>
> The biggest part is material (at first material is level; after the line I have a bishop for a pawn), worth +1.56; it changes after Bxa6 (my move 2 of the line).
>
> My first look didn't see the rank of your most advanced passed pawn (g2) coming; that costs me -0.65 once the line plays out; it changes after hxg2 (your move 2 of the line).
>
> The squares your pawns stand on turns against me over the line (-0.58); it changes after hxg2 (your move 2 of the line).
>
> My first look was counting on your pawns sitting on the same colour as your bishop, which goes away in the line (-0.48); it changes after Bxa6 (my move 2 of the line).

Every sentence is generated from the attribution numbers. There is no hand-written commentary anywhere in `outputs/`.

## Why I built it

I play chess and I do interpretability work, and engines are the obvious place where the two meet. An evaluation function is a model. Asking "what is this model paying attention to, and is it right" is the same question I'd ask of any network, except here I can check the answer against my own chess judgment. The "what did I get wrong" mode came out of that: the static evaluation is the model's first impression, the search is ground truth a few plies deeper, and the difference between them is exactly the model's error, which I can attribute feature by feature.

Nothing here depends on a chess library. The move generator, search, network, training loop and attribution code are all in this repo. python-chess appears only in the tests, as an independent oracle to cross-check my move generator.

## How it works

`board.py` is a 10x12 mailbox board with full legal move generation: castling, en passant, promotions, pins, checks, checkmate, stalemate, the fifty-move rule and threefold repetition. Make and unmake update a Zobrist hash incrementally. Perft from the start position gives 20, 400, 8,902, 197,281 and 4,865,609 for depths 1 to 5, and Kiwipete gives 48, 2,039, 97,862 and 4,085,603 for depths 1 to 4. Those match the published counts. The tests also walk 40 random games against python-chess and compare the full legal move list, the FEN, check status and repetition state at every position.

`features.py` computes 107 named features from the side to move's point of view: material counts, piece-square sums, mobility per piece type, king shelter and open files and attackers near the king, doubled and isolated and backward and passed pawns, pawn islands, bishop pair, rooks on open files and on the seventh, outposts, hanging and pinned pieces, centre control, space, and two endgame king terms. Each exists twice, once for me and once for you, plus game phase, the material balance and a bias. The extractor also records evidence for each feature, the actual squares and pieces, so the explainer can say "your passed pawn on g2" instead of "passed_pawns_theirs".

`eval.py` is the network, written in NumPy with forward, backward and input gradients by hand. It has a linear skip connection plus one hidden layer of 32 tanh units, and it's antisymmetric by construction: `score(x) = g(x) - g(swap(x))`, where `swap` exchanges my features and yours. The same position scores +s from one side and -s from the other, exactly, and the empty feature vector scores zero. The linear weights start at the classical material values and piece-square tables, and the hidden layer's output weights start at zero, so an untrained network is precisely the textbook evaluation. Training then moves every weight.

`search.py` is iterative deepening alpha-beta with a transposition table, MVV-LVA capture ordering, two killer moves per ply, quiescence search, check extension, mate-distance scoring and a full principal variation that runs through the quiescence line. That last detail matters: the leaf at the end of the PV is the exact position whose static score became the search result, which is what makes the attributions honest. The test suite verifies that the leaf's static evaluation equals the search score.

`explain.py` does the attribution. Integrated Gradients is implemented directly: a midpoint Riemann sum along the straight path from an all-zero baseline to the leaf's features, doubling the number of steps until the attributions sum to the network output within 1e-5. The completeness error is checked in the tests and printed in the outputs (a few millionths of a pawn). Group ablation is computed alongside it: zero every feature in a group, re-evaluate, report the change. The discrepancy mode uses the root position's features as the baseline instead of zeros, so the attributions sum to the change in evaluation along the line, and it records the ply at which each feature changed most so it can name the move.

`train.py` is TD-Leaf. The engine plays itself at depth 2 from a few random opening moves. For each move it keeps the leaf of the principal variation and trains that leaf's evaluation toward the TD(lambda) return of the later search scores, with the game result as the terminal value and the trajectory cut wherever an exploratory random move was played. Adam, gradient clipping, a small replay buffer of recent games, lambda 0.7.

## What training did

The committed weights in `outputs/eval_net.npz` come from a single run of 31 minutes on 2 cores: 148 self-play games, 15,616 training positions. The log is in `outputs/training_log.txt`. The mean squared TD error on the replay buffer fell from 10.6 to 0.21 over the run, though most of that is the early games where the terminal values dominate.

I then played the trained network against the untrained one (pure material plus piece-square tables, the exact initialization) and against a plain material counter, 20 games each at depth 2 with paired random openings. Full tables are in `outputs/match_results.md`.

Trained vs untrained initialization: 13 out of 20 (10 wins, 6 draws, 4 losses). Trained vs material only: 16.5 out of 20 (15 wins, 3 draws, 2 losses).

Twenty games is a small sample. The 65% against the initialization works out to roughly +108 Elo with a 95% interval close to plus or minus 178, so I'd call it "probably better, clearly no worse." The learned linear weights are chess-sensible where I've checked them: knights on the rim went to -0.23 pawns, hanging pieces to -0.09, the bishop pair to +0.20, a rook on an open file to +0.15, each extra pawn island to -0.16. The hidden layer has also learned some things I wouldn't endorse. In the self-play game it credits itself for the opponent's rook on the seventh rank, and in the Philidor position it likes the opponent controlling the centre. The attributions make these quirks visible, which is the point.

## How strong it is

Weak. It's a Python program computing 107 features per leaf, so in the benchmark run it managed between 5,300 nodes per second in Kiwipete and 15,000 in a rook endgame, and a good deal less when the machine was busy (the self-play game was annotated at around 3,000). Depth 4 takes half a second in the endgame and 16 seconds in Kiwipete; depth 5 takes 3 to 54 seconds. The exact table is `outputs/benchmarks.md`. It finds mates in 2 instantly and has no idea about anything past its horizon. My guess is that it plays around the level of a casual club beginner, somewhere in the 1000 to 1300 range at a few seconds a move, and I would not bet on the upper end. It beats a material-only search at the same depth most of the time, and that's the strongest claim I'm willing to make.

## Things to look at

`outputs/self_game.md` is a complete game the engine played against itself at depth 4 with an explanation after all 79 plies. It ends in 40. Qb7# after a pawn promotion. `outputs/examples.md` has five famous positions (the Greek gift from Colle vs O'Hanlon, a king-and-pawn endgame, the Philidor position, a smothered mate, and Kiwipete) with both explanation modes, the attribution table and the ablation table for each.

## Running it

Install and play (you type SAN or UCI moves; the engine explains every move it makes):

- `pip install -r requirements.txt`
- `python play.py --color white --depth 4`
- `python play.py --color black --seconds 5 --verbose`

Inside `play.py`, `why` explains the current position from your side, and `wrong` runs the discrepancy mode.

As a UCI engine (works in Arena, Cute Chess, and so on; switch on the `Explain` option to get the explanation as `info string` lines):

- `python uci.py`

Tests, training, matches and reports:

- `python -m pytest -q tests`
- `python train.py --minutes 30 --depth 2 --workers 2`
- `python match.py --opponent init --games 20 --depth 2`
- `python match.py --opponent material --games 20 --depth 2 --append`
- `python report.py bench`
- `python report.py examples --depth 4`
- `python report.py selfgame --depth 4 --seconds 8`
- `./run.sh` (all of the above, about an hour on 2 cores)

The tests cover perft, the python-chess cross-check, FEN round trips, make/unmake and incremental hashing, checkmate and draw detection, SAN, mate finding, transposition-table consistency (with the table used as a pure cache, a fixed-depth search returns the same score as a search with no table), the leaf-equals-score property, network antisymmetry, finite-difference gradient checks, Integrated Gradients completeness within 1e-4, that the explainer's sentences name the top attributed concepts with the right numbers, and the UCI handshake. 59 tests, about 50 seconds.

## Files

- `board.py` board, move generation, FEN, SAN, Zobrist, perft
- `features.py` the feature registry and extractor
- `eval.py` the NumPy network and the material-only baseline
- `search.py` alpha-beta, transposition table, quiescence, PV
- `explain.py` Integrated Gradients, ablation, English rendering, discrepancy mode
- `train.py` TD-Leaf self-play training
- `match.py` fixed-depth matches with paired openings
- `play.py` terminal play
- `uci.py` UCI protocol
- `report.py` generates the files in `outputs/`
- `tests/` pytest suite
- `outputs/eval_net.npz` trained weights
- `outputs/training_log.txt`, `outputs/training_log.jsonl`
- `outputs/match_results.md`
- `outputs/benchmarks.md`
- `outputs/examples.md`
- `outputs/self_game.md`

## Limits I know about

The zero baseline for Integrated Gradients means my eight pawns and your eight pawns each get a large attribution that cancels; the explainer nets the two halves of every concept before it speaks, and the attribution tables show both halves. The features are hand-designed and there are things the network literally cannot see, like whether a piece is trapped. Thirty minutes of depth-2 self-play is a very small amount of training, and the network is 107 inputs and 32 hidden units. Training runs against a wall-clock budget, so rerunning `run.sh` gives different weights and slightly different sentences from the ones committed here. And the search is slow enough that none of this would matter in a real game against a real engine.

MIT licensed.
