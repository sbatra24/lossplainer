# Match results

## Trained network vs untrained network (material + piece-square tables)

Fixed depth 2 plus quiescence, 20 games with paired random openings, 7.9 minutes of wall time on 2 cores.

Score for the trained network: **13 / 20** (10 wins, 6 draws, 4 losses, 65%).
Implied Elo difference: about +108 with a 95% interval of roughly +-178 (a normal approximation; 20 games is a small sample).

| game | trained plays | opening | result | plies | ended by | final material (trained side) |
|---|---|---|---|---|---|---|
| 1 | White | b4 Nh6 d3 g5 Bxg5 | 1-0 | 140 | checkmate | I have a queen and 2 pawns for a rook |
| 2 | Black | b4 Nh6 d3 g5 Bxg5 | 1-0 | 130 | checkmate | I'm down 2 queens, a bishop and a pawn |
| 3 | White | g4 Nf6 h3 g5 e3 | 0-1 | 167 | checkmate | I'm down a queen, a rook and a pawn |
| 4 | Black | g4 Nf6 h3 g5 e3 | 1/2-1/2 | 69 | threefold repetition | you have a bishop and a knight for 3 pawns |
| 5 | White | f4 e6 h4 a5 Nh3 Ba3 d3 Qg5 | 1-0 | 33 | checkmate | I have a queen, a bishop and a pawn for a knight |
| 6 | Black | f4 e6 h4 a5 Nh3 Ba3 d3 Qg5 | 1-0 | 67 | checkmate | you have a queen, a rook and a pawn for a knight |
| 7 | White | a4 b5 e4 h6 Ra3 | 0-1 | 181 | checkmate | I'm down a queen and a knight |
| 8 | Black | a4 b5 e4 h6 Ra3 | 1/2-1/2 | 37 | threefold repetition | you have 2 rooks and a pawn for a bishop |
| 9 | White | h4 e5 Nc3 d6 Nf3 | 1-0 | 124 | checkmate | I'm up 2 queens, a rook and a pawn |
| 10 | Black | h4 e5 Nc3 d6 Nf3 | 1/2-1/2 | 200 | truncated at move limit | I'm down a rook, a bishop and a pawn |
| 11 | White | c4 d6 a3 Nc6 | 1/2-1/2 | 200 | truncated at move limit | I'm down a knight and a pawn |
| 12 | Black | c4 d6 a3 Nc6 | 0-1 | 58 | checkmate | I'm up a pawn |
| 13 | White | h3 f6 Rh2 Nc6 | 1-0 | 87 | checkmate | I'm up a queen, 2 rooks, a bishop and a knight |
| 14 | Black | h3 f6 Rh2 Nc6 | 0-1 | 76 | checkmate | I have a knight for a pawn |
| 15 | White | f3 Nf6 Na3 Ng8 | 1/2-1/2 | 200 | truncated at move limit | I have a queen for a pawn |
| 16 | Black | f3 Nf6 Na3 Ng8 | 0-1 | 66 | checkmate | I have a rook and a bishop for a pawn |
| 17 | White | Nc3 e5 Nh3 d5 Nxd5 Bf5 | 1/2-1/2 | 200 | truncated at move limit | I'm down a knight and 3 pawns |
| 18 | Black | Nc3 e5 Nh3 d5 Nxd5 Bf5 | 0-1 | 124 | checkmate | I'm up 2 rooks and 2 pawns |
| 19 | White | e3 d6 d3 Nc6 b4 Nd4 Kd2 | 1-0 | 40 | checkmate | I'm up a knight |
| 20 | Black | e3 d6 d3 Nc6 b4 Nd4 Kd2 | 0-1 | 135 | checkmate | I have a queen, 2 rooks and 2 pawns for a knight |

## Trained network vs pure material count

Fixed depth 2 plus quiescence, 20 games with paired random openings, 5.5 minutes of wall time on 2 cores.

Score for the trained network: **16.5 / 20** (15 wins, 3 draws, 2 losses, 82%).
Implied Elo difference: about +269 with a 95% interval of roughly +-357 (a normal approximation; 20 games is a small sample).

| game | trained plays | opening | result | plies | ended by | final material (trained side) |
|---|---|---|---|---|---|---|
| 1 | White | b4 Nh6 d3 g5 Bxg5 | 1-0 | 18 | checkmate | I'm up 2 pawns |
| 2 | Black | b4 Nh6 d3 g5 Bxg5 | 1/2-1/2 | 133 | insufficient material | I'm up a knight |
| 3 | White | g4 Nf6 h3 g5 e3 | 1-0 | 86 | checkmate | you have a rook for a knight and a pawn |
| 4 | Black | g4 Nf6 h3 g5 e3 | 1/2-1/2 | 200 | truncated at move limit | I'm down a pawn |
| 5 | White | f4 e6 h4 a5 Nh3 Ba3 d3 Qg5 | 1-0 | 49 | checkmate | I'm up a queen and a rook |
| 6 | Black | f4 e6 h4 a5 Nh3 Ba3 d3 Qg5 | 1-0 | 85 | checkmate | I'm down a queen, a rook, a knight and 2 pawns |
| 7 | White | a4 b5 e4 h6 Ra3 | 1/2-1/2 | 91 | threefold repetition | I have a bishop for a knight |
| 8 | Black | a4 b5 e4 h6 Ra3 | 0-1 | 175 | checkmate | I'm up a rook, a knight and 3 pawns |
| 9 | White | h4 e5 Nc3 d6 Nf3 | 1-0 | 84 | checkmate | I'm up a rook and 3 pawns |
| 10 | Black | h4 e5 Nc3 d6 Nf3 | 1-0 | 110 | checkmate | I'm down a queen, a rook, a bishop and 3 pawns |
| 11 | White | c4 d6 a3 Nc6 | 1-0 | 91 | checkmate | I'm up a queen, 2 rooks and 5 pawns |
| 12 | Black | c4 d6 a3 Nc6 | 0-1 | 122 | checkmate | I'm up 2 rooks |
| 13 | White | h3 f6 Rh2 Nc6 | 1-0 | 187 | checkmate | I'm up 2 queens, a rook and a pawn |
| 14 | Black | h3 f6 Rh2 Nc6 | 0-1 | 94 | checkmate | I have a queen and 3 pawns for a rook, a bishop and a knight |
| 15 | White | f3 Nf6 Na3 Ng8 | 1-0 | 69 | checkmate | I have a rook and 3 pawns for a knight |
| 16 | Black | f3 Nf6 Na3 Ng8 | 0-1 | 96 | checkmate | I have a queen, a rook, a knight and a pawn for a bishop |
| 17 | White | Nc3 e5 Nh3 d5 Nxd5 Bf5 | 1-0 | 141 | checkmate | I have 2 queens for 2 pawns |
| 18 | Black | Nc3 e5 Nh3 d5 Nxd5 Bf5 | 0-1 | 86 | checkmate | I'm up a rook, a bishop and 3 pawns |
| 19 | White | e3 d6 d3 Nc6 b4 Nd4 Kd2 | 1-0 | 120 | checkmate | I'm up 2 rooks, a knight and 2 pawns |
| 20 | Black | e3 d6 d3 Nc6 b4 Nd4 Kd2 | 0-1 | 69 | checkmate | I'm up a queen, a rook and a pawn |

