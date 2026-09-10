# Five famous positions, explained by the engine

Every block below is the verbatim output of `explain()` and `explain_discrepancy()` at depth 4 using `outputs/eval_net.npz`. Nothing is hand-edited.

## Greek gift: Colle vs O'Hanlon, Nice 1930, before 12.Bxh7+

FEN: `r1bqr1k1/pp1n1ppp/3bp3/8/3pB3/2P2N2/PP3PPP/R1BQR1K1 w - - 0 12`  (White to move, so "I" is White)

```
8  r . b q r . k .
7  p p . n . p p p
6  . . . b p . . .
5  . . . . . . . .
4  . . . p B . . .
3  . . P . . N . .
2  P P . . . P P P
1  R . B Q R . K .
   a b c d e f g h
```

The textbook bishop sacrifice on h7. Colle played 12.Bxh7+ Kxh7 13.Ng5+ and won. A depth-limited engine with a tiny network will not see the whole combination; the point is to read what it does and doesn't value here.

Search: depth 4, 57,776 nodes in 9.1s (6,361 nodes/s), score +0.26.

### What the engine says

> I'm winning by about 0.3 pawn.
>
> I'm expecting 12. cxd4 Qb6 13. Qc2 Nf6, after which material is level.
>
> The biggest reason is my rook on the half-open e-file (+0.35).
>
> The squares my pawns stand on (+0.18) also counts for me.
>
> My pawns being split into 3 islands works against me (-0.26), but that's worth less than my rook on the half-open e-file.
>
> By theme: placement +0.21, mobility +0.19, pieces +0.16, pawn structure -0.14, center -0.10, threats +0.10.

### What its first impression got wrong

> At a glance I thought this position was -0.77. After searching 4 plies ahead I make it +0.26 (a swing of +1.03).
>
> The line I expect is 12. cxd4 Qb6 13. Qc2 Nf6.
>
> The biggest part is material (at first I'm down a pawn; after the line material is level), worth +0.61; it changes after cxd4 (my move 1 of the line).
>
> The squares my pawns stand on improves for me over the line (+0.34); it changes after cxd4 (my move 1 of the line).
>
> The squares your pawns stand on improves for me over the line (+0.30); it changes after cxd4 (my move 1 of the line).
>
> My first look didn't see my pawns being split into 3 islands coming; that costs me -0.20 once the line plays out; it changes after cxd4 (my move 1 of the line).

### Top attributions at the end of the line (Integrated Gradients, pawns)

```
concept                     net     mine   theirs   evidence
rook_semi_open_file      +0.353   +0.353   -0.000   mine: e-file
pawn_islands             -0.264   -0.762   +0.498   
pawn_pst                 +0.177   +0.651   -0.473   
bishop_pair              -0.120   +0.560   -0.680   
attacked_by_lower        +0.097   +0.097   -0.000   mine: Be4
isolated_pawns           +0.076   +0.076   -0.000   mine: d4
queen_mobility           +0.075   +0.279   -0.204   
bias                     -0.073   -0.073   +0.000   
phase                    -0.070   -0.070   +0.000   
bad_bishop_pawns         -0.068   -0.765   +0.696   
```

Completeness check: attributions sum to the network output with error 2.8e-06 (128 integration steps).

### Group ablation (score change when the group's features are zeroed)

```
placement        +0.177
pawn_structure   -0.173
mobility         +0.168
king_safety      -0.102
material         +0.090
center           -0.065
threats          -0.039
pieces           +0.004
endgame          +0.001
development      -0.001
passed_pawns     +0.000
```

## King and pawn endgame: king in front of its passed pawn

FEN: `8/5k2/8/3PK3/8/8/8/8 w - - 0 1`  (White to move, so "I" is White)

```
8  . . . . . . . .
7  . . . . . k . .
6  . . . . . . . .
5  . . . P K . . .
4  . . . . . . . .
3  . . . . . . . .
2  . . . . . . . .
1  . . . . . . . .
   a b c d e f g h
```

White wins with the king ahead of the pawn. The only thing that matters is the passed pawn and the kings, so this is a clean test of the passed-pawn and king features.

Search: depth 4, 422 nodes in 0.0s (18,620 nodes/s), score +3.94.

### What the engine says

> I'm winning by about 3.9 pawns.
>
> I'm expecting 1. d6 Ke8 2. Ke6 Kf8, after which I'm up a pawn.
>
> The biggest reason is where my king stands (+1.29).
>
> The rank of my most advanced passed pawn (d6) (+0.63) and my king being centralised for the endgame (+0.47) also count for me.
>
> My pawns forming a single group works against me (-0.32), but that's worth less than where my king stands.
>
> By theme: placement +1.65, passed pawns +1.27, endgame +0.63, material +0.44, king safety -0.11, center -0.07, pawn structure +0.05.

### What its first impression got wrong

> At a glance I thought this position was +3.17. After searching 4 plies ahead I make it +3.94 (a swing of +0.77).
>
> The line I expect is 1. d6 Ke8 2. Ke6 Kf8.
>
> Where your king stands improves for me over the line (+0.49); it changes after Ke8 (your move 1 of the line).
>
> Your king being centralised for the endgame improves for me over the line (+0.24); it changes after Ke8 (your move 1 of the line).
>
> My king being centralised for the endgame turns against me over the line (-0.21); it changes after Ke6 (my move 2 of the line).
>
> Where my king stands turns against me over the line (-0.19); it changes after Ke6 (my move 2 of the line).

### Top attributions at the end of the line (Integrated Gradients, pawns)

```
concept                     net     mine   theirs   evidence
king_pst                 +1.291   +0.673   +0.618   
pawns                    +0.996   +0.996   -0.000   
best_passer_rank         +0.634   +0.634   -0.000   mine: d6
king_centralization      +0.465   +0.465   -0.000   
passed_advancement       +0.416   +0.416   -0.000   mine: d6
material_balance         -0.360   -0.360   +0.000   
pawn_pst                 +0.360   +0.360   -0.000   
pawn_islands             -0.324   -0.324   +0.000   
passed_pawns             +0.217   +0.217   -0.000   mine: d6
pawns_advanced           +0.213   +0.213   -0.000   
```

Completeness check: attributions sum to the network output with error 2.6e-06 (256 integration steps).

### Group ablation (score change when the group's features are zeroed)

```
placement        +1.504
passed_pawns     +1.206
endgame          +0.607
material         +0.567
king_safety      -0.097
pawn_structure   +0.037
center           +0.022
development      +0.000
mobility         +0.000
pieces           +0.000
threats          +0.000
```

## Philidor position (rook endgame, Black holds the draw)

FEN: `4k3/7R/r7/4K3/4P3/8/8/8 b - - 0 1`  (Black to move, so "I" is Black)

```
8  . . . . k . . .
7  . . . . . . . R
6  r . . . . . . .
5  . . . . K . . .
4  . . . . P . . .
3  . . . . . . . .
2  . . . . . . . .
1  . . . . . . . .
   a b c d e f g h
```

Black keeps the rook on the third rank until the pawn advances, then checks from behind. Theoretically drawn; the engine's search is far too shallow to know that, so the explanation shows what a material+structure network thinks a pawn-up rook endgame is worth.

Search: depth 4, 4,780 nodes in 0.3s (18,278 nodes/s), score -2.61.

### What the engine says

> I'm losing by about 2.6 pawns.
>
> I'm expecting 1... Kf8 2. Rc7 Kg8 3. Kd4, after which I'm down a pawn.
>
> The biggest reason is where your king stands (-1.00).
>
> Your king being centralised for the endgame (-0.50) and the material (I'm down a pawn) (-0.48) also count against me.
>
> Your control of the central squares works in my favour (+0.39), but that's worth less than where your king stands.
>
> By theme: placement -1.29, passed pawns -0.69, endgame -0.66, material -0.48, pieces +0.39, center +0.19, pawn structure +0.15, king safety -0.14.

### What its first impression got wrong

> At a glance I thought this position was -2.61. After searching 4 plies ahead I make it -2.61 (a swing of +0.00).
>
> My first impression was about right; the line 1... Kf8 2. Rc7 Kg8 3. Kd4 doesn't change much.

### Top attributions at the end of the line (Integrated Gradients, pawns)

```
concept                     net     mine   theirs   evidence
pawns                    -1.005   +0.000   -1.005   
king_pst                 -0.997   -0.418   -0.579   
king_centralization      -0.499   +0.000   -0.499   
center_control           +0.392   -0.000   +0.392   
rook_on_seventh          +0.377   -0.000   +0.377   theirs: c7
material_balance         +0.333   +0.333   +0.000   
pawn_islands             +0.289   -0.000   +0.289   
best_passer_rank         -0.275   +0.000   -0.275   theirs: e4
pawn_pst                 -0.258   +0.000   -0.258   
space                    -0.255   -0.130   -0.125   
```

Completeness check: attributions sum to the network output with error 3.8e-06 (256 integration steps).

### Group ablation (score change when the group's features are zeroed)

```
placement        -1.192
passed_pawns     -0.608
material         -0.489
endgame          -0.444
pawn_structure   +0.144
mobility         +0.093
pieces           +0.040
center           +0.034
king_safety      -0.032
development      +0.000
threats          +0.000
```

## Smothered mate pattern (Philidor's legacy): Qg8+ Rxg8, Nf7#

FEN: `r2q1r1k/pp4pp/4Q2N/8/8/8/PP3PPP/6K1 w - - 0 1`  (White to move, so "I" is White)

```
8  r . . q . r . k
7  p p . . . . p p
6  . . . . Q . . N
5  . . . . . . . .
4  . . . . . . . .
3  . . . . . . . .
2  P P . . . P P P
1  . . . . . . K .
   a b c d e f g h
```

A forced mate in two. This shows the explainer's short-circuit: when the search finds a mate the network's features are irrelevant and the engine says so, and the discrepancy mode reports that a static evaluation cannot see mates.

Search: depth 3, 456 nodes in 0.0s (12,870 nodes/s), score mate in 2.

### What the engine says

> I have a forced mate in 2.
>
> The line is 1. Qg8+ Rxg8 2. Nf7#. No need to weigh features when the king is the issue.

### What its first impression got wrong

> At a glance I thought this position was -2.84. After searching 3 plies ahead I make it mate in 2 (a swing of +101.84).
>
> The static evaluation cannot see a mate; the line is 1. Qg8+.

## Kiwipete (the standard move-generator test position)

FEN: `r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1`  (White to move, so "I" is White)

```
8  r . . . k . . r
7  p . p p q p b .
6  b n . . p n p .
5  . . . P N . . .
4  . p . . P . . .
3  . . N . . Q . p
2  P P P B B P P P
1  R . . . K . . R
   a b c d e f g h
```

A wild middlegame with every special move type available. Perft from here is how the move generator was validated; the explanation shows how the network weighs a messy position.

Search: depth 4, 88,631 nodes in 12.4s (7,169 nodes/s), score +0.35.

### What the engine says

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

### What its first impression got wrong

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

### Top attributions at the end of the line (Integrated Gradients, pawns)

```
concept                     net     mine   theirs   evidence
bishops                  +3.250   +6.457   -3.208   
pawns                    -0.840   +5.983   -6.823   
best_passer_rank         -0.766   +0.000   -0.766   theirs: g2
bishop_pair              +0.627   +0.627   -0.000   
material_balance         -0.602   -0.602   +0.000   
rook_semi_open_file      -0.378   +0.000   -0.378   theirs: h-file
pawns_advanced           -0.369   +0.000   -0.369   
passed_advancement       -0.343   +0.000   -0.343   theirs: g2
bad_bishop_pawns         -0.325   -0.782   +0.457   
material_total           -0.299   -6.819   +6.520   
```

Completeness check: attributions sum to the network output with error 5.1e-06 (256 integration steps).

### Group ablation (score change when the group's features are zeroed)

```
material         +1.616
passed_pawns     -0.973
pawn_structure   -0.455
pieces           -0.130
placement        +0.096
mobility         +0.077
center           +0.077
king_safety      -0.064
threats          -0.037
endgame          -0.015
development      +0.000
```
