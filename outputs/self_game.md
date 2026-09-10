# The engine plays itself and explains every move

Trained network on both sides, depth 4 with a 8s soft limit per move. Each explanation is the engine speaking as the side that just moved, about the position it expects after its principal variation.

Result: **1-0** after 79 plies, 927,237 nodes, 5.3 minutes.

```
1. e4 d5 2. e5 d4 3. Bb5+ Bd7 4. Bxd7+ Nxd7 5. Nf3 e6 6. d3 Bb4+ 7. Bd2 Qe7 8. a3 Bc5 9. b4 Bb6 10. O-O a6 11. Qe2 f6 12. Bf4 g5 13. exf6 Ngxf6 14. Nxg5 e5 15. Re1 Rg8 16. Bxe5 O-O-O 17. Bxf6 Qxe2 18. Rxe2 Nxf6 19. h4 Rde8 20. Rxe8+ Rxe8 21. Nd2 Ng4 22. h5 Re2 23. Nge4 Ne3 24. Rb1 Kb8 25. h6 Kc8 26. a4 Ba7 27. a5 Kb8 28. g3 c6 29. g4 b5 30. g5 Kb7 31. g6 hxg6 32. h7 Nxc2 33. h8=Q Re1+ 34. Rxe1 Nxe1 35. Qd8 c5 36. bxc5 Bxc5 37. Qd7+ Ka8 38. Nxc5 Nf3+ 39. Nxf3 b4 40. Qb7#
```

### 1. e4

`rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`  depth 4, 6,625 nodes, 2,596 n/s, eval +0.05

> This looks about equal (+0.05).
>
> I'm expecting 1. e4 d5 2. e5 Nc6, after which material is level.
>
> What I have going for me: your control of the central squares (+0.21). What you have: the squares my knights stand on (-0.48). They roughly cancel.

### 1... d5

`rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1`  depth 4, 7,900 nodes, 2,849 n/s, eval -0.36

> I'm losing by about 0.4 pawn.
>
> I'm expecting 1... d5 2. e5 d4 3. Qf3, after which material is level.
>
> The biggest reason is how much room your queen has (-0.27).
>
> Where my queen stands (-0.21) also counts against me.
>
> By theme: mobility -0.32, placement -0.16, king safety +0.09, material +0.08, center -0.07.

### 2. e5

`rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2`  depth 4, 12,453 nodes, 2,900 n/s, eval +0.06

> This looks about equal (+0.06).
>
> I'm expecting 2. e5 d4 3. Nf3 Nc6, after which material is level.
>
> Nothing in the position stands out to me; every factor is small.

### 2... d4

`rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2`  depth 4, 7,167 nodes, 2,578 n/s, eval -0.31

> I'm losing by about 0.3 pawn.
>
> I'm expecting 2... d4 3. Nf3 e6 4. d3, after which material is level.
>
> The biggest reason is the squares my knights stand on (-0.47).
>
> By theme: placement -0.46, mobility +0.12, development -0.05.

### 3. Bb5+

`rnbqkbnr/ppp1pppp/8/4P3/3p4/8/PPPP1PPP/RNBQKBNR w KQkq - 0 3`  depth 4, 13,016 nodes, 2,610 n/s, eval +0.10

> This looks about equal (+0.10).
>
> I'm expecting 3. Bb5+ Bd7 4. Bd3 e6 5. Nf3, after which material is level.
>
> What I have going for me: the squares your knights stand on (+0.49). What you have: the squares your pawns stand on (-0.24). They roughly cancel.

### 3... Bd7

`rnbqkbnr/ppp1pppp/8/1B2P3/3p4/8/PPPP1PPP/RNBQK1NR b KQkq - 1 3`  depth 4, 17,782 nodes, 2,491 n/s, eval -0.04

> This looks about equal (-0.04).
>
> I'm expecting 3... Bd7 4. Bxd7+ Nxd7 5. Nf3 e6 6. d3, after which material is level.
>
> Nothing in the position stands out to me; every factor is small.

### 4. Bxd7+

`rn1qkbnr/pppbpppp/8/1B2P3/3p4/8/PPPP1PPP/RNBQK1NR w KQkq - 2 4`  depth 4, 265 nodes, 10,978 n/s, eval +0.04

> This looks about equal (+0.04).
>
> I'm expecting 4. Bxd7+ Nxd7 5. Nf3 e6, after which material is level.

### 4... Nxd7

`rn1qkbnr/pppBpppp/8/4P3/3p4/8/PPPP1PPP/RNBQK1NR b KQkq - 0 4`  depth 4, 9,248 nodes, 3,047 n/s, eval +0.13

> This looks about equal (+0.13).
>
> I'm expecting 4... Nxd7 5. Nf3 e6 6. d3 Bc5, after which material is level.
>
> Nothing in the position stands out to me; every factor is small.

### 5. Nf3

`r2qkbnr/pppnpppp/8/4P3/3p4/8/PPPP1PPP/RNBQK1NR w KQkq - 0 5`  depth 4, 142 nodes, 94,736 n/s, eval -0.13

> This looks about equal (-0.13).
>
> I'm expecting 5. Nf3 e6 6. d3 Bc5, after which material is level.
>
> Nothing in the position stands out to me; every factor is small.

### 5... e6

`r2qkbnr/pppnpppp/8/4P3/3p4/5N2/PPPP1PPP/RNBQK2R b KQkq - 1 5`  depth 4, 7,103 nodes, 2,510 n/s, eval +0.00

> This looks about equal (+0.00).
>
> I'm expecting 5... e6 6. d3 Bb4+ 7. Bd2 Qe7, after which material is level.

### 6. d3

`r2qkbnr/pppn1ppp/4p3/4P3/3p4/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 6`  depth 4, 11,892 nodes, 2,222 n/s, eval -0.06

> This looks about equal (-0.06).
>
> I'm expecting 6. d3 Be7 7. Nbd2 a6, after which material is level.
>
> What I have going for me: the squares your knights stand on (+0.51). What you have: my pawns sitting on the same colour as my bishop (-0.15). They roughly cancel.

### 6... Bb4+

`r2qkbnr/pppn1ppp/4p3/4P3/3p4/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 6`  depth 4, 24,447 nodes, 2,442 n/s, eval -0.03

> This looks about equal (-0.03).
>
> I'm expecting 6... Bb4+ 7. Bd2 Qe7 8. b3 Kf8 9. Bxb4 Qxb4+ 10. Nbd2, after which material is level.
>
> What I have going for me: how much room my queen has (+0.22). What you have: the squares my knights stand on (-0.58). They roughly cancel.

### 7. Bd2

`r2qk1nr/pppn1ppp/4p3/4P3/1b1p4/3P1N2/PPP2PPP/RNBQK2R w KQkq - 1 7`  depth 4, 24,728 nodes, 2,688 n/s, eval +0.08

> This looks about equal (+0.08).
>
> I'm expecting 7. Bd2 Qe7 8. Qe2 Qc5 9. Qe4, after which material is level.
>
> Nothing in the position stands out to me; every factor is small.

### 7... Qe7

`r2qk1nr/pppn1ppp/4p3/4P3/1b1p4/3P1N2/PPPB1PPP/RN1QK2R b KQkq - 2 7`  depth 4, 527 nodes, 5,491 n/s, eval -0.08

> This looks about equal (-0.08).
>
> I'm expecting 7... Qe7 8. Qe2 Qc5 9. Qe4, after which material is level.
>
> Nothing in the position stands out to me; every factor is small.

### 8. a3

`r3k1nr/pppnqppp/4p3/4P3/1b1p4/3P1N2/PPPB1PPP/RN1QK2R w KQkq - 3 8`  depth 4, 23,418 nodes, 2,331 n/s, eval +0.25

> I'm winning by about 0.2 pawn.
>
> I'm expecting 8. a3 Bc5 9. c3 dxc3 10. Nxc3, after which material is level.
>
> The biggest reason is the squares your knights stand on (+0.60).
>
> The squares my pawns stand on (+0.20) and my pawns across the middle of the board (+0.17) also count for me.
>
> My pawns sitting on the same colour as my bishop works against me (-0.30), but that's worth less than the squares your knights stand on.
>
> By theme: placement +0.68, pieces -0.30, pawn structure +0.17, center -0.14, mobility -0.12, development +0.09, material -0.07.

### 8... Bc5

`r3k1nr/pppnqppp/4p3/4P3/1b1p4/P2P1N2/1PPB1PPP/RN1QK2R b KQkq - 0 8`  depth 4, 12,723 nodes, 2,961 n/s, eval -0.29

> I'm losing by about 0.3 pawn.
>
> I'm expecting 8... Bc5 9. b4 Bb6 10. b5, after which material is level.
>
> The biggest reason is your pawns across the middle of the board (-0.18).
>
> How much room my queen has works in my favour (+0.13), but that's worth less than your pawns across the middle of the board.
>
> By theme: pawn structure -0.27, placement +0.11.

### 9. b4

`r3k1nr/pppnqppp/4p3/2b1P3/3p4/P2P1N2/1PPB1PPP/RN1QK2R w KQkq - 1 9`  depth 4, 17,830 nodes, 2,089 n/s, eval +0.22

> I'm winning by about 0.2 pawn.
>
> I'm expecting 9. b4 Bb6 10. Bg5 Qf8, after which material is level.
>
> My pawns sitting on the same colour as my bishop works against me (-0.14), but that's worth less than the rest.
>
> By theme: mobility +0.14, pieces -0.14, center +0.09.

### 9... Bb6

`r3k1nr/pppnqppp/4p3/2b1P3/1P1p4/P2P1N2/2PB1PPP/RN1QK2R b KQkq - 0 9`  depth 4, 7,259 nodes, 2,647 n/s, eval -0.17

> I'm losing by about 0.2 pawn.
>
> I'm expecting 9... Bb6 10. c3 dxc3 11. Nxc3, after which material is level.
>
> The biggest reason is the squares my knights stand on (-0.61).
>
> Your pawns across the middle of the board (-0.17) also counts against me.
>
> Your pawns sitting on the same colour as your bishop works in my favour (+0.29), but that's worth less than the squares my knights stand on.
>
> By theme: placement -0.57, pieces +0.29, pawn structure -0.17, center +0.14, mobility +0.14, development -0.09.

### 10. O-O

`r3k1nr/pppnqppp/1b2p3/4P3/1P1p4/P2P1N2/2PB1PPP/RN1QK2R w KQkq - 1 10`  depth 4, 29,022 nodes, 2,025 n/s, eval +0.29

> I'm winning by about 0.3 pawn.
>
> I'm expecting 10. O-O a6 11. Bg5 Qf8, after which material is level.
>
> The biggest reason is where my king stands (+0.48).
>
> The pawn shelter in front of my king (+0.19) also counts for me.
>
> My pawns sitting on the same colour as my bishop works against me (-0.29), but that's worth less than where my king stands.
>
> By theme: placement +0.52, pieces -0.29, king safety -0.14, mobility +0.08, pawn structure +0.08.

### 10... a6

`r3k1nr/pppnqppp/1b2p3/4P3/1P1p4/P2P1N2/2PB1PPP/RN1Q1RK1 b kq - 2 10`  depth 4, 11,180 nodes, 2,671 n/s, eval -0.14

> This looks about equal (-0.14).
>
> I'm expecting 10... a6 11. Bf4 g6 12. Nbd2, after which material is level.
>
> What I have going for me: your pawns sitting on the same colour as your bishop (+0.41). What you have: the squares my knights stand on (-0.54). They roughly cancel.

### 11. Qe2

`r3k1nr/1ppnqppp/pb2p3/4P3/1P1p4/P2P1N2/2PB1PPP/RN1Q1RK1 w kq - 0 11`  depth 4, 29,133 nodes, 2,154 n/s, eval +0.20

> I'm winning by about 0.2 pawn.
>
> I'm expecting 11. Qe2 f6 12. Re1 fxe5 13. Nxe5 Nxe5 14. Qxe5, after which material is level.
>
> The biggest reason is where my king stands (+0.43).
>
> My rook on the half-open e-file (+0.41) and the pawn shelter in front of my king (+0.36) also count for me.
>
> My control of the central squares works against me (-0.27), but that's worth less than where my king stands.
>
> By theme: mobility +0.43, placement +0.36, center -0.27, pieces +0.24, pawn structure -0.22, material -0.22, king safety -0.14.

### 11... f6

`r3k1nr/1ppnqppp/pb2p3/4P3/1P1p4/P2P1N2/2PBQPPP/RN3RK1 b kq - 1 11`  depth 4, 12,878 nodes, 2,301 n/s, eval -0.20

> I'm losing by about 0.2 pawn.
>
> I'm expecting 11... f6 12. Re1 fxe5 13. Nxe5 Nxe5 14. Qxe5, after which material is level.
>
> The biggest reason is where your king stands (-0.43).
>
> Your rook on the half-open e-file (-0.41) and the pawn shelter in front of your king (-0.36) also count against me.
>
> Your control of the central squares works in my favour (+0.27), but that's worth less than where your king stands.
>
> By theme: mobility -0.43, placement -0.36, center +0.27, pieces -0.24, pawn structure +0.22, material +0.22, king safety +0.14.

### 12. Bf4

`r3k1nr/1ppnq1pp/pb2pp2/4P3/1P1p4/P2P1N2/2PBQPPP/RN3RK1 w kq - 0 12`  depth 4, 19,068 nodes, 2,111 n/s, eval +0.18

> I'm winning by about 0.2 pawn.
>
> I'm expecting 12. Bf4 g5 13. Bd2 fxe5 14. Nxe5, after which material is level.
>
> The biggest reason is where my king stands (+0.49).
>
> The pawn shelter in front of my king (+0.40) and the squares your knights stand on (+0.17) also count for me.
>
> My king being castled works against me (-0.27), but that's worth less than where my king stands.
>
> By theme: placement +0.52, pawn structure -0.19, pieces -0.17, center +0.06, king safety -0.05.

### 12... g5

`r3k1nr/1ppnq1pp/pb2pp2/4P3/1P1p1B2/P2P1N2/2P1QPPP/RN3RK1 b kq - 1 12`  depth 4, 18,279 nodes, 1,949 n/s, eval -0.15

> I'm losing by about 0.1 pawn.
>
> I'm expecting 12... g5 13. exf6 Ngxf6 14. Nxg5, after which I'm down a pawn.
>
> The biggest reason is the material (I'm down a pawn) (-0.65).
>
> Where your king stands (-0.49) and the pawn shelter in front of your king (-0.44) also count against me.
>
> The squares your knights stand on works in my favour (+0.58), but that's worth less than the material (I'm down a pawn).
>
> By theme: material -0.65, pawn structure +0.29, pieces +0.28, placement +0.19, center -0.10, development +0.09, mobility -0.07.

### 13. exf6

`r3k1nr/1ppnq2p/pb2pp2/4P1p1/1P1p1B2/P2P1N2/2P1QPPP/RN3RK1 w kq - 0 13`  depth 4, 9,637 nodes, 2,440 n/s, eval +0.10

> This looks about equal (+0.10).
>
> I'm expecting 13. exf6 Ngxf6 14. Be5 Nxe5 15. Nxe5, after which you have a bishop for a knight.
>
> What I have going for me: where my king stands (+0.43). What you have: the squares my knights stand on (-0.34). They roughly cancel.

### 13... Ngxf6

`r3k1nr/1ppnq2p/pb2pP2/6p1/1P1p1B2/P2P1N2/2P1QPPP/RN3RK1 b kq - 0 13`  depth 4, 8,410 nodes, 3,329 n/s, eval -0.12

> This looks about equal (-0.12).
>
> I'm expecting 13... Ngxf6 14. Bxg5 Rg8 15. Re1, after which I'm down a pawn.
>
> What I have going for me: the squares your knights stand on (+0.51). What you have: the material (I'm down a pawn) (-0.63). They roughly cancel.

### 14. Nxg5

`r3k2r/1ppnq2p/pb2pn2/6p1/1P1p1B2/P2P1N2/2P1QPPP/RN3RK1 w kq - 0 14`  depth 4, 22,798 nodes, 2,240 n/s, eval +0.51

> I'm winning by about 0.5 pawn.
>
> I'm expecting 14. Nxg5 Nd5 15. Qh5+ Kd8 16. Nf7+ Kc8 17. Nxh8 Nxf4, after which I have a rook and a pawn for a bishop.
>
> The biggest reason is the material (I have a rook and a pawn for a bishop) (+0.92).
>
> How much room your knights have (+0.35) and the pawn shelter in front of my king (+0.33) also count for me.
>
> The squares my knights stand on works against me (-1.25), but that's worth less than the material (I have a rook and a pawn for a bishop).
>
> By theme: placement -1.22, material +0.92, mobility +0.48, king safety +0.37, center +0.32, pawn structure -0.26, pieces -0.14, development -0.10.

### 14... e5

`r3k2r/1ppnq2p/pb2pn2/6N1/1P1p1B2/P2P4/2P1QPPP/RN3RK1 b kq - 0 14`  depth 4, 24,892 nodes, 2,521 n/s, eval -0.62

> I'm losing by about 0.6 pawn.
>
> I'm expecting 14... e5 15. Re1 Rg8 16. Bxe5 Rxg5 17. Bxf6, after which I'm down 2 pawns.
>
> The biggest reason is the material (I'm down 2 pawns) (-1.43).
>
> The pawn shelter in front of your king (-0.83) and where your king stands (-0.44) also count against me.
>
> The squares your knights stand on works in my favour (+0.52), but that's worth less than the material (I'm down 2 pawns).
>
> By theme: material -1.43, pieces +0.56, mobility +0.41, king safety -0.35, pawn structure +0.29, threats +0.17, center -0.14, development +0.14, passed pawns -0.12, placement +0.10.

### 15. Re1

`r3k2r/1ppnq2p/pb3n2/4p1N1/1P1p1B2/P2P4/2P1QPPP/RN3RK1 w kq - 0 15`  depth 4, 15,693 nodes, 2,492 n/s, eval +0.55

> I'm winning by about 0.6 pawn.
>
> I'm expecting 15. Re1 Rf8 16. Bxe5 Nd5, after which I'm up 2 pawns.
>
> The biggest reason is the material (I'm up 2 pawns) (+1.35).
>
> The pawn shelter in front of my king (+0.77) and where my king stands (+0.50) also count for me.
>
> The squares my knights stand on works against me (-0.71), but that's worth less than the material (I'm up 2 pawns).
>
> By theme: material +1.35, pieces -0.49, pawn structure -0.30, mobility -0.29, king safety +0.28, placement -0.25, passed pawns +0.12, development -0.11.

### 15... Rg8

`r3k2r/1ppnq2p/pb3n2/4p1N1/1P1p1B2/P2P4/2P1QPPP/RN2R1K1 b kq - 1 15`  depth 4, 46,883 nodes, 2,121 n/s, eval -0.69

> I'm losing by about 0.7 pawn.
>
> I'm expecting 15... Rg8 16. h4 Nd5 17. Bxe5, after which I'm down 2 pawns.
>
> The biggest reason is the material (I'm down 2 pawns) (-1.42).
>
> The pawn shelter in front of your king (-0.54) and where your king stands (-0.51) also count against me.
>
> The squares your knights stand on works in my favour (+0.73), but that's worth less than the material (I'm down 2 pawns).
>
> By theme: material -1.42, pieces +0.46, placement +0.34, pawn structure +0.30, mobility +0.12, king safety -0.12, passed pawns -0.11, development +0.10, center -0.08, threats -0.08.

### 16. Bxe5

`r3k1r1/1ppnq2p/pb3n2/4p1N1/1P1p1B2/P2P4/2P1QPPP/RN2R1K1 w q - 2 16`  depth 4, 29,223 nodes, 2,322 n/s, eval +1.01

> I'm winning by about 1.0 pawn.
>
> I'm expecting 16. Bxe5 O-O-O 17. f4 Rg6, after which I'm up 2 pawns.
>
> The biggest reason is the material (I'm up 2 pawns) (+1.51).
>
> Where my king stands (+0.33) and the rank of my most advanced passed pawn (f4) (+0.31) also count for me.
>
> The squares my knights stand on works against me (-0.59), but that's worth less than the material (I'm up 2 pawns).
>
> By theme: material +1.51, passed pawns +0.54, placement -0.53, pieces -0.52, pawn structure -0.25, center +0.13, development -0.10, threats +0.09, king safety +0.08.

### 16... O-O-O

`r3k1r1/1ppnq2p/pb3n2/4B1N1/1P1p4/P2P4/2P1QPPP/RN2R1K1 b q - 0 16`  depth 4, 11,419 nodes, 2,595 n/s, eval -0.96

> I'm losing by about 1.0 pawn.
>
> I'm expecting 16... O-O-O 17. Bf4 Qxe2 18. Rxe2, after which I'm down 2 pawns.
>
> The biggest reason is the material (I'm down 2 pawns) (-1.49).
>
> The pawn shelter in front of your king (-0.26) and where your king stands (-0.22) also count against me.
>
> The squares your knights stand on works in my favour (+0.65), but that's worth less than the material (I'm down 2 pawns).
>
> By theme: material -1.49, placement +0.66, pieces +0.38, pawn structure +0.34, mobility -0.29, king safety -0.24, passed pawns -0.18, development +0.10, center -0.10.

### 17. Bxf6

`2kr2r1/1ppnq2p/pb3n2/4B1N1/1P1p4/P2P4/2P1QPPP/RN2R1K1 w - - 1 17`  depth 4, 19,916 nodes, 2,598 n/s, eval +0.76

> I'm winning by about 0.8 pawn.
>
> I'm expecting 17. Bxf6 Qxe2 18. Rxe2 Nxf6, after which I have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (I have a knight and 2 pawns for a bishop) (+1.50).
>
> Your pawns sitting on the same colour as your bishop (+0.24) and my passed pawn on f2 (+0.23) also count for me.
>
> The squares my knights stand on works against me (-0.58), but that's worth less than the material (I have a knight and 2 pawns for a bishop).
>
> By theme: material +1.50, placement -0.65, pawn structure -0.35, passed pawns +0.23, center +0.22, mobility -0.13, development -0.12, threats -0.09.

### 17... Qxe2

`2kr2r1/1ppnq2p/pb3B2/6N1/1P1p4/P2P4/2P1QPPP/RN2R1K1 b - - 0 17`  depth 4, 3,811 nodes, 3,012 n/s, eval -1.03

> I'm losing by about 1.0 pawn.
>
> I'm expecting 17... Qxe2 18. Rxe2 Nxf6 19. f4, after which you have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (you have a knight and 2 pawns for a bishop) (-1.49).
>
> The rank of your most advanced passed pawn (f4) (-0.28) and my pawns sitting on the same colour as my bishop (-0.24) also count against me.
>
> The squares your knights stand on works in my favour (+0.57), but that's worth less than the material (you have a knight and 2 pawns for a bishop).
>
> By theme: material -1.49, placement +0.75, passed pawns -0.72, pawn structure +0.38, king safety +0.12, center -0.12, development +0.11, mobility +0.08.

### 18. Rxe2

`2kr2r1/1ppn3p/pb3B2/6N1/1P1p4/P2P4/2P1qPPP/RN2R1K1 w - - 0 18`  depth 4, 2,173 nodes, 3,915 n/s, eval +0.67

> I'm winning by about 0.7 pawn.
>
> I'm expecting 18. Rxe2 Nxf6 19. Re5 Rd5, after which I have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (I have a knight and 2 pawns for a bishop) (+1.52).
>
> Your pawns sitting on the same colour as your bishop (+0.24) and the pawn shelter in front of my king (+0.21) also count for me.
>
> The squares my knights stand on works against me (-0.60), but that's worth less than the material (I have a knight and 2 pawns for a bishop).
>
> By theme: material +1.52, placement -0.60, pawn structure -0.36, mobility -0.33, center +0.23, passed pawns +0.20, development -0.12, threats -0.10, king safety +0.09.

### 18... Nxf6

`2kr2r1/1ppn3p/pb3B2/6N1/1P1p4/P2P4/2P1RPPP/RN4K1 b - - 0 18`  depth 4, 5,529 nodes, 2,981 n/s, eval -0.86

> I'm losing by about 0.9 pawn.
>
> I'm expecting 18... Nxf6 19. Ne6 Rde8 20. Nd2, after which you have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (you have a knight and 2 pawns for a bishop) (-1.47).
>
> My pawns sitting on the same colour as my bishop (-0.23) and your passed pawn on f2 (-0.22) also count against me.
>
> My rook on the half-open g-file works in my favour (+0.40), but that's worth less than the material (you have a knight and 2 pawns for a bishop).
>
> By theme: material -1.47, mobility +0.46, pawn structure +0.37, passed pawns -0.22, pieces +0.14, king safety -0.08, threats +0.07.

### 19. h4

`2kr2r1/1pp4p/pb3n2/6N1/1P1p4/P2P4/2P1RPPP/RN4K1 w - - 0 19`  depth 4, 10,036 nodes, 3,178 n/s, eval +0.58

> I'm winning by about 0.6 pawn.
>
> I'm expecting 19. h4 Kb8 20. Nd2 Rde8 21. Rxe8+ Rxe8 22. Nxh7 Nxh7, after which you have a bishop for 3 pawns.
>
> The biggest reason is the squares your knights stand on (+0.62).
>
> My passed pawns on f2, g2 and h4 (+0.58) and your knight on the edge of the board (h7) (+0.46) also count for me.
>
> The pawn shelter in front of your king works against me (-0.38), but that's worth less than the squares your knights stand on.
>
> By theme: passed pawns +1.06, pieces +0.58, pawn structure -0.57, mobility -0.44, placement +0.44, king safety -0.37, material -0.33, endgame +0.05.

### 19... Rde8

`2kr2r1/1pp4p/pb3n2/6N1/1P1p3P/P2P4/2P1RPP1/RN4K1 b - - 0 19`  depth 4, 13,160 nodes, 2,808 n/s, eval -0.55

> I'm losing by about 0.6 pawn.
>
> I'm expecting 19... Rde8 20. Ne4 Nxe4 21. dxe4, after which you have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (you have a knight and 2 pawns for a bishop) (-1.49).
>
> Your passed pawns on f2 and e4 (-0.38) and the rank of your most advanced passed pawn (e4) (-0.27) also count against me.
>
> My rook on the half-open e-file and g-file works in my favour (+0.72), but that's worth less than the material (you have a knight and 2 pawns for a bishop).
>
> By theme: material -1.49, passed pawns -0.85, mobility +0.60, pieces +0.57, placement +0.36, pawn structure +0.27, king safety +0.18, center -0.16, development +0.13, threats +0.08.

### 20. Rxe8+

`2k1r1r1/1pp4p/pb3n2/6N1/1P1p3P/P2P4/2P1RPP1/RN4K1 w - - 1 20`  depth 4, 6,437 nodes, 3,245 n/s, eval +0.98

> I'm winning by about 1.0 pawn.
>
> I'm expecting 20. Rxe8+ Rxe8 21. Nd2 Re2 22. Rd1, after which I have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (I have a knight and 2 pawns for a bishop) (+1.22).
>
> Your rook on the seventh rank (e2) (+0.46) and your pawns sitting on the same colour as your bishop (+0.24) also count for me.
>
> The squares your pawns stand on works against me (-0.29), but that's worth less than the material (I have a knight and 2 pawns for a bishop).
>
> By theme: material +1.22, pieces +0.56, mobility -0.45, pawn structure -0.41, passed pawns +0.20, center +0.17, placement -0.14, king safety -0.13, endgame -0.09.

### 20... Rxe8

`2k1R1r1/1pp4p/pb3n2/6N1/1P1p3P/P2P4/2P2PP1/RN4K1 b - - 0 20`  depth 4, 5,084 nodes, 3,624 n/s, eval -0.79

> I'm losing by about 0.8 pawn.
>
> I'm expecting 20... Rxe8 21. Nd2 Re2 22. Nxh7 Nxh7, after which I have a bishop for 3 pawns.
>
> The biggest reason is the squares my knights stand on (-0.62).
>
> Your passed pawns on f2, g2 and h4 (-0.58) and my knight on the edge of the board (h7) (-0.50) also count against me.
>
> The material (I have a bishop for 3 pawns) works in my favour (+0.38), but that's worth less than the squares my knights stand on.
>
> By theme: passed pawns -1.04, pieces -1.01, pawn structure +0.56, placement -0.52, material +0.38, mobility +0.34, king safety +0.22, center +0.11, threats +0.11, endgame +0.06.

### 21. Nd2

`2k1r3/1pp4p/pb3n2/6N1/1P1p3P/P2P4/2P2PP1/RN4K1 w - - 0 21`  depth 4, 128 nodes, 13,008 n/s, eval +0.79

> I'm winning by about 0.8 pawn.
>
> I'm expecting 21. Nd2 Re2 22. Nxh7 Nxh7, after which you have a bishop for 3 pawns.
>
> The biggest reason is the squares your knights stand on (+0.62).
>
> My passed pawns on f2, g2 and h4 (+0.58) and your knight on the edge of the board (h7) (+0.50) also count for me.
>
> The material (you have a bishop for 3 pawns) works against me (-0.38), but that's worth less than the squares your knights stand on.
>
> By theme: passed pawns +1.04, pieces +1.01, pawn structure -0.56, placement +0.52, material -0.38, mobility -0.34, king safety -0.22, center -0.11, threats -0.11, endgame -0.06.

### 21... Ng4

`2k1r3/1pp4p/pb3n2/6N1/1P1p3P/P2P4/2PN1PP1/R5K1 b - - 1 21`  depth 4, 10,830 nodes, 3,064 n/s, eval -1.23

> I'm losing by about 1.2 pawn.
>
> I'm expecting 21... Ng4 22. h5 Ne3 23. Re1, after which you have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (you have a knight and 2 pawns for a bishop) (-1.29).
>
> My pawns sitting on the same colour as my bishop (-0.22) and your passed pawn on f2 (-0.20) also count against me.
>
> My knight on e3 being attacked by something cheaper works in my favour (+0.23), but that's worth less than the material (you have a knight and 2 pawns for a bishop).
>
> By theme: material -1.29, mobility +0.31, king safety +0.20, pawn structure +0.20, passed pawns -0.20, pieces -0.20, center -0.17, placement +0.07, endgame -0.05.

### 22. h5

`2k1r3/1pp4p/pb6/6N1/1P1p2nP/P2P4/2PN1PP1/R5K1 w - - 2 22`  depth 4, 9,585 nodes, 2,959 n/s, eval +1.04

> I'm winning by about 1.0 pawn.
>
> I'm expecting 22. h5 Ne3 23. Re1 Rg8, after which I have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (I have a knight and 2 pawns for a bishop) (+1.44).
>
> Your pawns sitting on the same colour as your bishop (+0.23) and my pawn attacking your knight on e3 (+0.21) also count for me.
>
> Your rook on the half-open g-file works against me (-0.40), but that's worth less than the material (I have a knight and 2 pawns for a bishop).
>
> By theme: material +1.44, mobility -0.26, king safety -0.24, pawn structure -0.22, passed pawns +0.20, threats -0.09, center +0.07, endgame +0.06, pieces -0.05.

### 22... Re2

`2k1r3/1pp4p/pb6/6NP/1P1p2n1/P2P4/2PN1PP1/R5K1 b - - 0 22`  depth 4, 19,082 nodes, 3,204 n/s, eval -1.08

> I'm losing by about 1.1 pawn.
>
> I'm expecting 22... Re2 23. Nde4 h6 24. f3, after which you have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (you have a knight and 2 pawns for a bishop) (-1.22).
>
> My rook on the seventh rank (e2) (-0.37) and my pawns sitting on the same colour as my bishop (-0.37) also count against me.
>
> The squares my pawns stand on works in my favour (+0.47), but that's worth less than the material (you have a knight and 2 pawns for a bishop).
>
> By theme: material -1.22, pieces -0.94, mobility +0.43, king safety +0.43, passed pawns -0.38, pawn structure +0.28, placement +0.09, endgame +0.08.

### 23. Nge4

`2k5/1pp4p/pb6/6NP/1P1p2n1/P2P4/2PNrPP1/R5K1 w - - 1 23`  depth 4, 7,109 nodes, 2,993 n/s, eval +1.44

> I'm winning by about 1.4 pawn.
>
> I'm expecting 23. Nge4 Ne3 24. fxe3 dxe3, after which I have 2 knights and a pawn for a bishop.
>
> The biggest reason is the material (I have 2 knights and a pawn for a bishop) (+2.53).
>
> My knight outpost on e4 (+0.39) and your rook on the seventh rank (e2) (+0.37) also count for me.
>
> How much room my knights have works against me (-0.72), but that's worth less than the material (I have 2 knights and a pawn for a bishop).
>
> By theme: material +2.53, pieces +1.04, passed pawns -0.82, mobility -0.70, king safety -0.38, center +0.12, pawn structure -0.08, endgame -0.07, threats -0.05.

### 23... Ne3

`2k5/1pp4p/pb6/7P/1P1pN1n1/P2P4/2PNrPP1/R5K1 b - - 2 23`  depth 4, 6,213 nodes, 3,442 n/s, eval -1.22

> I'm losing by about 1.2 pawn.
>
> I'm expecting 23... Ne3 24. Rc1 Kb8 25. fxe3 dxe3, after which you have 2 knights and a pawn for a bishop.
>
> The biggest reason is the material (you have 2 knights and a pawn for a bishop) (-2.56).
>
> Your knight outpost on e4 (-0.39) and my rook on the seventh rank (e2) (-0.37) also count against me.
>
> How much room your knights have works in my favour (+0.69), but that's worth less than the material (you have 2 knights and a pawn for a bishop).
>
> By theme: material -2.56, pieces -1.05, passed pawns +0.81, mobility +0.71, king safety +0.52, center -0.13, placement +0.12, endgame +0.09, pawn structure +0.07.

### 24. Rb1

`2k5/1pp4p/pb6/7P/1P1pN3/P2Pn3/2PNrPP1/R5K1 w - - 3 24`  depth 4, 10,110 nodes, 2,934 n/s, eval +1.33

> I'm winning by about 1.3 pawn.
>
> I'm expecting 24. Rb1 Kb8 25. fxe3 dxe3, after which I have 2 knights and a pawn for a bishop.
>
> The biggest reason is the material (I have 2 knights and a pawn for a bishop) (+2.55).
>
> My knight outpost on e4 (+0.39) and your rook on the seventh rank (e2) (+0.37) also count for me.
>
> How much room my knights have works against me (-0.64), but that's worth less than the material (I have 2 knights and a pawn for a bishop).
>
> By theme: material +2.55, pieces +1.05, passed pawns -0.82, mobility -0.57, king safety -0.52, center +0.13, placement -0.13, endgame -0.08, pawn structure -0.08.

### 24... Kb8

`2k5/1pp4p/pb6/7P/1P1pN3/P2Pn3/2PNrPP1/1R4K1 b - - 4 24`  depth 4, 8,773 nodes, 2,739 n/s, eval -1.22

> I'm losing by about 1.2 pawn.
>
> I'm expecting 24... Kb8 25. Rc1 Ng4 26. Rd1, after which you have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (you have a knight and 2 pawns for a bishop) (-1.21).
>
> My rook on the seventh rank (e2) (-0.45) and your knight outpost on e4 (-0.35) also count against me.
>
> The number of attacks on the squares around your king works in my favour (+0.24), but that's worth less than the material (you have a knight and 2 pawns for a bishop).
>
> By theme: material -1.21, pieces -0.89, king safety +0.55, mobility +0.31, pawn structure +0.19, passed pawns -0.18, center -0.08, endgame +0.06.

### 25. h6

`1k6/1pp4p/pb6/7P/1P1pN3/P2Pn3/2PNrPP1/1R4K1 w - - 5 25`  depth 4, 15,110 nodes, 2,645 n/s, eval +1.50

> I'm winning by about 1.5 pawns.
>
> I'm expecting 25. h6 Ba7 26. fxe3 dxe3, after which I have 2 knights and a pawn for a bishop.
>
> The biggest reason is the material (I have 2 knights and a pawn for a bishop) (+2.58).
>
> My knight outpost on e4 (+0.40) and your rook on the seventh rank (e2) (+0.37) also count for me.
>
> How much room my knights have works against me (-0.62), but that's worth less than the material (I have 2 knights and a pawn for a bishop).
>
> By theme: material +2.58, pieces +1.05, passed pawns -0.82, mobility -0.54, king safety -0.53, center +0.13, endgame -0.07, pawn structure -0.07, placement -0.06.

### 25... Kc8

`1k6/1pp4p/pb5P/8/1P1pN3/P2Pn3/2PNrPP1/1R4K1 b - - 0 25`  depth 4, 14,250 nodes, 3,057 n/s, eval -1.28

> I'm losing by about 1.3 pawn.
>
> I'm expecting 25... Kc8 26. Rc1 Kb8 27. fxe3 dxe3, after which you have 2 knights and a pawn for a bishop.
>
> The biggest reason is the material (you have 2 knights and a pawn for a bishop) (-2.55).
>
> Your knight outpost on e4 (-0.39) and my rook on the seventh rank (e2) (-0.37) also count against me.
>
> How much room your knights have works in my favour (+0.70), but that's worth less than the material (you have 2 knights and a pawn for a bishop).
>
> By theme: material -2.55, pieces -1.04, passed pawns +0.81, mobility +0.71, king safety +0.52, center -0.13, endgame +0.08, pawn structure +0.07, placement +0.06.

### 26. a4

`2k5/1pp4p/pb5P/8/1P1pN3/P2Pn3/2PNrPP1/1R4K1 w - - 1 26`  depth 4, 14,095 nodes, 2,973 n/s, eval +1.61

> I'm winning by about 1.6 pawns.
>
> I'm expecting 26. a4 Kb8 27. a5 Ba7 28. fxe3 dxe3, after which I have 2 knights and a pawn for a bishop.
>
> The biggest reason is the material (I have 2 knights and a pawn for a bishop) (+2.56).
>
> My knight outpost on e4 (+0.39) and your rook on the seventh rank (e2) (+0.37) also count for me.
>
> How much room my knights have works against me (-0.62), but that's worth less than the material (I have 2 knights and a pawn for a bishop).
>
> By theme: material +2.56, pieces +1.04, passed pawns -0.81, mobility -0.54, king safety -0.51, pawn structure +0.12, center +0.11, placement -0.08, endgame -0.06.

### 26... Ba7

`2k5/1pp4p/pb5P/8/PP1pN3/3Pn3/2PNrPP1/1R4K1 b - - 0 26`  depth 4, 12,008 nodes, 3,229 n/s, eval -1.45

> I'm losing by about 1.4 pawn.
>
> I'm expecting 26... Ba7 27. Rc1 Kb8 28. a5, after which you have a knight and 2 pawns for a bishop.
>
> The biggest reason is the material (you have a knight and 2 pawns for a bishop) (-1.21).
>
> My rook on the seventh rank (e2) (-0.41) and your knight outpost on e4 (-0.34) also count against me.
>
> The number of attacks on the squares around your king works in my favour (+0.23), but that's worth less than the material (you have a knight and 2 pawns for a bishop).
>
> By theme: material -1.21, pieces -0.84, king safety +0.44, passed pawns -0.17, mobility +0.12, placement +0.08.

### 27. a5

`2k5/bpp4p/p6P/8/PP1pN3/3Pn3/2PNrPP1/1R4K1 w - - 1 27`  depth 4, 15,697 nodes, 2,921 n/s, eval +1.61

> I'm winning by about 1.6 pawns.
>
> I'm expecting 27. a5 Kb8 28. fxe3 dxe3, after which I have 2 knights and a pawn for a bishop.
>
> The biggest reason is the material (I have 2 knights and a pawn for a bishop) (+2.56).
>
> My knight outpost on e4 (+0.39) and your rook on the seventh rank (e2) (+0.37) also count for me.
>
> How much room my knights have works against me (-0.62), but that's worth less than the material (I have 2 knights and a pawn for a bishop).
>
> By theme: material +2.56, pieces +1.04, passed pawns -0.81, mobility -0.54, king safety -0.51, pawn structure +0.12, center +0.11, placement -0.08, endgame -0.06.

### 27... Kb8

`2k5/bpp4p/p6P/P7/1P1pN3/3Pn3/2PNrPP1/1R4K1 b - - 0 27`  depth 4, 8,465 nodes, 2,813 n/s, eval -1.51

> I'm losing by about 1.5 pawns.
>
> I'm expecting 27... Kb8 28. b5 axb5 29. Rxb5 Nxc2, after which you have a knight and a pawn for a bishop.
>
> The biggest reason is the material (you have a knight and a pawn for a bishop) (-0.65).
>
> My rook on the seventh rank (e2) (-0.41) and your rook on the half-open b-file (-0.38) also count against me.
>
> How much room your knights have works in my favour (+0.30), but that's worth less than the material (you have a knight and a pawn for a bishop).
>
> By theme: pieces -1.17, material -0.65, king safety +0.26, passed pawns -0.22, pawn structure +0.11, threats -0.11, center +0.07.

### 28. g3

`1k6/bpp4p/p6P/P7/1P1pN3/3Pn3/2PNrPP1/1R4K1 w - - 1 28`  depth 4, 14,008 nodes, 2,757 n/s, eval +1.44

> I'm winning by about 1.4 pawn.
>
> I'm expecting 28. g3 b5 29. fxe3 dxe3, after which I have 2 knights and a pawn for a bishop.
>
> The biggest reason is the material (I have 2 knights and a pawn for a bishop) (+2.51).
>
> Your rook on the seventh rank (e2) (+0.39) and my knight outpost on e4 (+0.38) also count for me.
>
> How much room my knights have works against me (-0.58), but that's worth less than the material (I have 2 knights and a pawn for a bishop).
>
> By theme: material +2.51, pieces +1.04, passed pawns -0.84, mobility -0.56, king safety -0.46, placement -0.17, pawn structure +0.14, center +0.10, threats -0.05, endgame -0.05.

### 28... c6

`1k6/bpp4p/p6P/P7/1P1pN3/3Pn1P1/2PNrP2/1R4K1 b - - 0 28`  depth 4, 10,803 nodes, 3,437 n/s, eval -1.37

> I'm losing by about 1.4 pawn.
>
> I'm expecting 28... c6 29. Rc1 c5 30. bxc5 Bxc5 31. fxe3 dxe3, after which you have 2 knights and a pawn for a bishop.
>
> The biggest reason is the material (you have 2 knights and a pawn for a bishop) (-2.47).
>
> My rook on the seventh rank (e2) (-0.36) and the squares your knights stand on (-0.33) also count against me.
>
> How much room your knights have works in my favour (+0.65), but that's worth less than the material (you have 2 knights and a pawn for a bishop).
>
> By theme: material -2.47, pieces -0.81, mobility +0.80, king safety +0.46, passed pawns +0.30, threats +0.16, placement +0.12, center -0.11.

### 29. g4

`1k6/bp5p/p1p4P/P7/1P1pN3/3Pn1P1/2PNrP2/1R4K1 w - - 0 29`  depth 4, 9,475 nodes, 5,620 n/s, eval +1.58

> I'm winning by about 1.6 pawns.
>
> I'm expecting 29. g4 b5 30. fxe3 dxe3, after which I have 2 knights and a pawn for a bishop.
>
> The biggest reason is the material (I have 2 knights and a pawn for a bishop) (+2.47).
>
> Your rook on the seventh rank (e2) (+0.46) and the blockade on your passed pawn on e3 (+0.34) also count for me.
>
> How much room my knights have works against me (-0.67), but that's worth less than the material (I have 2 knights and a pawn for a bishop).
>
> By theme: material +2.47, pieces +0.90, passed pawns -0.80, king safety -0.68, mobility -0.65, pawn structure +0.23, placement +0.18, center +0.18, threats -0.08.

### 29... b5

`1k6/bp5p/p1p4P/P7/1P1pN1P1/3Pn3/2PNrP2/1R4K1 b - - 0 29`  depth 4, 11,684 nodes, 5,724 n/s, eval -1.65

> I'm losing by about 1.6 pawns.
>
> I'm expecting 29... b5 30. g5 Nxc2 31. Kg2, after which you have a knight and a pawn for a bishop.
>
> The biggest reason is the material (you have a knight and a pawn for a bishop) (-0.74).
>
> My rook on the seventh rank (e2) (-0.53) and your pawns across the middle of the board (-0.43) also count against me.
>
> The pawn shelter in front of my king works in my favour (+0.53), but that's worth less than the material (you have a knight and a pawn for a bishop).
>
> By theme: pieces -0.81, material -0.74, king safety +0.44, center -0.31, placement -0.24, passed pawns -0.19, mobility +0.08, pawn structure -0.08, threats +0.06.

### 30. g5

`1k6/b6p/p1p4P/Pp6/1P1pN1P1/3Pn3/2PNrP2/1R4K1 w - b6 0 30`  depth 4, 8,607 nodes, 5,550 n/s, eval +1.87

> I'm winning by about 1.9 pawns.
>
> I'm expecting 30. g5 Kb7 31. g6 hxg6 32. fxe3 dxe3, after which I have 2 knights for a bishop.
>
> The biggest reason is the material (I have 2 knights for a bishop) (+1.78).
>
> Your rook on the seventh rank (e2) (+0.42) and the blockade on your passed pawn on e3 (+0.35) also count for me.
>
> How much room my knights have works against me (-0.62), but that's worth less than the material (I have 2 knights for a bishop).
>
> By theme: material +1.78, king safety -0.93, pieces +0.85, mobility -0.59, placement +0.34, pawn structure +0.31, passed pawns +0.15, center +0.15, threats -0.08, endgame +0.07.

### 30... Kb7

`1k6/b6p/p1p4P/Pp4P1/1P1pN3/3Pn3/2PNrP2/1R4K1 b - - 0 30`  depth 4, 7,804 nodes, 5,995 n/s, eval -2.19

> I'm losing by about 2.2 pawns.
>
> I'm expecting 30... Kb7 31. g6 hxg6 32. h7, after which you have a knight and a pawn for a bishop.
>
> The biggest reason is the squares your pawns stand on (-0.73).
>
> The rank of your most advanced passed pawn (h7) (-0.71) and the material (you have a knight and a pawn for a bishop) (-0.61) also count against me.
>
> The pawn shelter in front of my king works in my favour (+0.55), but that's worth less than the squares your pawns stand on.
>
> By theme: passed pawns -1.43, king safety +1.01, placement -0.88, pieces -0.69, material -0.61, threats +0.22, pawn structure +0.18, mobility -0.07.

### 31. g6

`8/bk5p/p1p4P/Pp4P1/1P1pN3/3Pn3/2PNrP2/1R4K1 w - - 1 31`  depth 4, 8,744 nodes, 7,045 n/s, eval +3.61

> I'm winning by about 3.6 pawns.
>
> I'm expecting 31. g6 hxg6 32. h7 Rxd2 33. Nxd2, after which I have a rook and a pawn for a bishop.
>
> The biggest reason is the material (I have a rook and a pawn for a bishop) (+1.32).
>
> The squares my pawns stand on (+0.81) and the rank of my most advanced passed pawn (h7) (+0.65) also count for me.
>
> The pawn shelter in front of your king works against me (-0.46), but that's worth less than the material (I have a rook and a pawn for a bishop).
>
> By theme: passed pawns +1.35, material +1.32, king safety -0.77, placement +0.65, mobility +0.50, center +0.29, endgame +0.27, pieces +0.15, threats -0.14, pawn structure -0.14.

### 31... hxg6

`8/bk5p/p1p3PP/Pp6/1P1pN3/3Pn3/2PNrP2/1R4K1 b - - 0 31`  depth 4, 5,727 nodes, 9,528 n/s, eval -3.61

> I'm losing by about 3.6 pawns.
>
> I'm expecting 31... hxg6 32. h7 Rxd2 33. Nxd2, after which you have a rook and a pawn for a bishop.
>
> The biggest reason is the material (you have a rook and a pawn for a bishop) (-1.32).
>
> The squares your pawns stand on (-0.81) and the rank of your most advanced passed pawn (h7) (-0.65) also count against me.
>
> The pawn shelter in front of my king works in my favour (+0.46), but that's worth less than the material (you have a rook and a pawn for a bishop).
>
> By theme: passed pawns -1.35, material -1.32, king safety +0.77, placement -0.65, mobility -0.50, center -0.29, endgame -0.27, pieces -0.15, threats +0.14, pawn structure +0.14.

### 32. h7

`8/bk6/p1p3pP/Pp6/1P1pN3/3Pn3/2PNrP2/1R4K1 w - - 0 32`  depth 4, 6,453 nodes, 7,611 n/s, eval +4.05

> I'm winning by about 4.0 pawns.
>
> I'm expecting 32. h7 Nxc2 33. h8=Q Re1+ 34. Rxe1 Nxe1, after which I have a queen and a knight for a bishop and a pawn.
>
> The biggest reason is the material (I have a queen and a knight for a bishop and a pawn) (+3.37).
>
> The squares my knights stand on (+0.72) and the space behind your pawns (+0.61) also count for me.
>
> Where my queen stands works against me (-0.62), but that's worth less than the material (I have a queen and a knight for a bishop and a pawn).
>
> By theme: material +3.37, center +0.61, king safety -0.34, endgame +0.32, mobility -0.24, placement +0.20, threats -0.14, pawn structure -0.09, pieces +0.06.

### 32... Nxc2

`8/bk5P/p1p3p1/Pp6/1P1pN3/3Pn3/2PNrP2/1R4K1 b - - 0 32`  depth 4, 6,193 nodes, 8,377 n/s, eval -4.05

> I'm losing by about 4.0 pawns.
>
> I'm expecting 32... Nxc2 33. h8=Q Re1+ 34. Rxe1 Nxe1, after which you have a queen and a knight for a bishop and a pawn.
>
> The biggest reason is the material (you have a queen and a knight for a bishop and a pawn) (-3.37).
>
> The squares your knights stand on (-0.72) and the space behind my pawns (-0.61) also count against me.
>
> Where your queen stands works in my favour (+0.62), but that's worth less than the material (you have a queen and a knight for a bishop and a pawn).
>
> By theme: material -3.37, center -0.61, king safety +0.34, endgame -0.32, mobility +0.24, placement -0.20, threats +0.14, pawn structure +0.09, pieces -0.06.

### 33. h8=Q

`8/bk5P/p1p3p1/Pp6/1P1pN3/3P4/2nNrP2/1R4K1 w - - 0 33`  depth 4, 9,022 nodes, 5,986 n/s, eval +4.85

> I'm winning by about 4.8 pawns.
>
> I'm expecting 33. h8=Q Re1+ 34. Rxe1 Nxe1 35. Qg7+ Kb8 36. Qxg6, after which I have a queen and a knight for a bishop.
>
> The biggest reason is the material (I have a queen and a knight for a bishop) (+3.60).
>
> The squares your knights stand on (+0.69) and the space behind your pawns (+0.68) also count for me.
>
> How much room my knights have works against me (-0.57), but that's worth less than the material (I have a queen and a knight for a bishop).
>
> By theme: material +3.60, center +0.76, placement +0.72, pawn structure -0.42, mobility -0.33, endgame +0.31, threats -0.06.

### 33... Re1+

`7Q/bk6/p1p3p1/Pp6/1P1pN3/3P4/2nNrP2/1R4K1 b - - 0 33`  depth 4, 6,196 nodes, 5,908 n/s, eval -5.04

> I'm losing by about 5.0 pawns.
>
> I'm expecting 33... Re1+ 34. Rxe1 Nxe1 35. Nc5+ Bxc5 36. Qg7+ Kb8 37. bxc5, after which you have a queen for a pawn.
>
> The biggest reason is the material (you have a queen for a pawn) (-3.21).
>
> The space behind my pawns (-0.51) and the squares my knights stand on (-0.45) also count against me.
>
> Your control of the central squares works in my favour (+0.22), but that's worth less than the material (you have a queen for a pawn).
>
> By theme: material -3.21, placement -0.61, passed pawns +0.48, center -0.46, pawn structure -0.35, endgame -0.31, king safety -0.31, mobility -0.13.

### 34. Rxe1

`7Q/bk6/p1p3p1/Pp6/1P1pN3/3P4/2nN1P2/1R2r1K1 w - - 1 34`  depth 4, 15,727 nodes, 8,089 n/s, eval +6.03

> I'm winning by about 6.0 pawns.
>
> I'm expecting 34. Rxe1 Nxe1 35. Qd8 Nf3+ 36. Nxf3 g5 37. Nxd4 Bxd4 38. Qxd4, after which I'm up a queen and a knight.
>
> The biggest reason is the material (I'm up a queen and a knight) (+4.13).
>
> The space behind your pawns (+0.99) and how far my king is from my pawns (+0.73) also count for me.
>
> How much room my knights have works against me (-0.63), but that's worth less than the material (I'm up a queen and a knight).
>
> By theme: material +4.13, endgame +0.76, center +0.68, placement +0.64, mobility -0.54, pieces -0.17, pawn structure +0.15, king safety -0.09.

### 34... Nxe1

`7Q/bk6/p1p3p1/Pp6/1P1pN3/3P4/2nN1P2/4R1K1 b - - 0 34`  depth 4, 71 nodes, 18,364 n/s, eval -6.03

> I'm losing by about 6.0 pawns.
>
> I'm expecting 34... Nxe1 35. Qd8 Nf3+ 36. Nxf3, after which you have a queen and 2 knights for a bishop and a pawn.
>
> The biggest reason is the material (you have a queen and 2 knights for a bishop and a pawn) (-4.51).
>
> The space behind my pawns (-0.85) and the squares your knights stand on (-0.45) also count against me.
>
> How much room your knights have works in my favour (+1.15), but that's worth less than the material (you have a queen and 2 knights for a bishop and a pawn).
>
> By theme: material -4.51, mobility +0.93, center -0.77, endgame -0.43, placement -0.41, pawn structure +0.11, king safety +0.09.

### 35. Qd8

`7Q/bk6/p1p3p1/Pp6/1P1pN3/3P4/3N1P2/4n1K1 w - - 0 35`  depth 4, 21,607 nodes, 9,364 n/s, eval +6.23

> I'm winning by about 6.2 pawns.
>
> I'm expecting 35. Qd8 c5 36. Qd7+ Kb8 37. Qd6+ Kb7 38. bxc5 Nxd3, after which I have a queen and a knight for a bishop and a pawn.
>
> The biggest reason is the material (I have a queen and a knight for a bishop and a pawn) (+3.47).
>
> How much room my queen has (+0.40) and the blockade on your passed pawn on d4 (+0.39) also count for me.
>
> Your passed pawns on d4 and b5 works against me (-0.21), but that's worth less than the material (I have a queen and a knight for a bishop and a pawn).
>
> By theme: material +3.47, pawn structure +0.70, placement +0.44, king safety +0.39, mobility +0.35, center +0.30, pieces +0.18, endgame +0.15, passed pawns +0.12, threats +0.07.

### 35... c5

`3Q4/bk6/p1p3p1/Pp6/1P1pN3/3P4/3N1P2/4n1K1 b - - 1 35`  depth 4, 5,778 nodes, 8,724 n/s, eval -6.23

> I'm losing by about 6.2 pawns.
>
> I'm expecting 35... c5 36. Qd7+ Kb8 37. Qd6+ Kb7 38. bxc5 Nxd3, after which you have a queen and a knight for a bishop and a pawn.
>
> The biggest reason is the material (you have a queen and a knight for a bishop and a pawn) (-3.47).
>
> How much room your queen has (-0.40) and the blockade on my passed pawn on d4 (-0.39) also count against me.
>
> My passed pawns on d4 and b5 works in my favour (+0.21), but that's worth less than the material (you have a queen and a knight for a bishop and a pawn).
>
> By theme: material -3.47, pawn structure -0.70, placement -0.44, king safety -0.39, mobility -0.35, center -0.30, pieces -0.18, endgame -0.15, passed pawns -0.12, threats -0.07.

### 36. bxc5

`3Q4/bk6/p5p1/Ppp5/1P1pN3/3P4/3N1P2/4n1K1 w - - 0 36`  depth 4, 29,156 nodes, 9,057 n/s, eval +6.52

> I'm winning by about 6.5 pawns.
>
> I'm expecting 36. bxc5 b4 37. Qd7+ Kb8 38. Qxd4, after which I have a queen, a knight and a pawn for a bishop.
>
> The biggest reason is the material (I have a queen, a knight and a pawn for a bishop) (+4.02).
>
> The space behind my pawns (+0.84) and the squares my knights stand on (+0.71) also count for me.
>
> My control of the central squares works against me (-0.54), but that's worth less than the material (I have a queen, a knight and a pawn for a bishop).
>
> By theme: material +4.02, placement +1.17, king safety +0.39, endgame +0.31, center +0.30, mobility -0.30, pawn structure +0.18, pieces +0.08, threats +0.07.

### 36... Bxc5

`3Q4/bk6/p5p1/PpP5/3pN3/3P4/3N1P2/4n1K1 b - - 0 36`  depth 4, 10,547 nodes, 8,746 n/s, eval -6.74

> I'm losing by about 6.7 pawns.
>
> I'm expecting 36... Bxc5 37. Nxc5+ Kc6 38. Qb6+ Kd5 39. Ndb3, after which you have a queen and a knight for a pawn.
>
> The biggest reason is the material (you have a queen and a knight for a pawn) (-4.42).
>
> The space behind my pawns (-0.73) and the squares my knights stand on (-0.68) also count against me.
>
> Where my king stands works in my favour (+0.57), but that's worth less than the material (you have a queen and a knight for a pawn).
>
> By theme: material -4.42, center -1.00, pawn structure -0.79, passed pawns +0.46, king safety -0.45, endgame -0.22, mobility +0.20, placement -0.17.

### 37. Qd7+

`3Q4/1k6/p5p1/Ppb5/3pN3/3P4/3N1P2/4n1K1 w - - 0 37`  depth 4, 26,485 nodes, 8,744 n/s, eval +7.25

> I'm winning by about 7.2 pawns.
>
> I'm expecting 37. Qd7+ Ka8 38. Nxc5 Nf3+ 39. Nxf3 b4 40. Nxd4, after which I'm up a queen and 2 knights.
>
> The biggest reason is the material (I'm up a queen and 2 knights) (+4.93).
>
> The space behind my pawns (+1.31) and my isolated pawns on f2, d3 and a5 (+0.57) also count for me.
>
> How much room my knights have works against me (-1.23), but that's worth less than the material (I'm up a queen and 2 knights).
>
> By theme: material +4.93, mobility -1.17, placement +1.07, center +0.91, passed pawns -0.48, pawn structure +0.46, king safety +0.46, endgame +0.38, threats +0.08.

### 37... Ka8

`8/1k1Q4/p5p1/Ppb5/3pN3/3P4/3N1P2/4n1K1 b - - 1 37`  depth 4, 2,077 nodes, 20,255 n/s, eval mated in 3

> I'm getting mated in 3.
>
> The line is 37... Ka8 38. Nxc5 Nf3+ 39. Nxf3 b4 40. Qb7#. No need to weigh features when the king is the issue.

### 38. Nxc5

`k7/3Q4/p5p1/Ppb5/3pN3/3P4/3N1P2/4n1K1 w - - 2 38`  depth 4, 296 nodes, 28,645 n/s, eval mate in 3

> I have a forced mate in 3.
>
> The line is 38. Nxc5. No need to weigh features when the king is the issue.

### 38... Nf3+

`k7/3Q4/p5p1/PpN5/3p4/3P4/3N1P2/4n1K1 b - - 0 38`  depth 4, 67 nodes, 11,240 n/s, eval mated in 2

> I'm getting mated in 2.
>
> The line is 38... Nf3+ 39. Nxf3 b4 40. Qb7#. No need to weigh features when the king is the issue.

### 39. Nxf3

`k7/3Q4/p5p1/PpN5/3p4/3P1n2/3N1P2/6K1 w - - 1 39`  depth 3, 15 nodes, 30,868 n/s, eval mate in 2

> I have a forced mate in 2.
>
> The line is 39. Nxf3. No need to weigh features when the king is the issue.

### 39... b4

`k7/3Q4/p5p1/PpN5/3p4/3P1N2/5P2/6K1 b - - 0 39`  depth 2, 16 nodes, 50,787 n/s, eval mated in 1

> I'm getting mated in 1.
>
> The line is 39... b4. No need to weigh features when the king is the issue.

### 40. Qb7#

`k7/3Q4/p5p1/P1N5/1p1p4/3P1N2/5P2/6K1 w - - 0 40`  depth 1, 38 nodes, 137,799 n/s, eval mate in 1

> I have a forced mate in 1.
>
> The line is 40. Qb7#. No need to weigh features when the king is the issue.

Final position: `k7/1Q6/p5p1/P1N5/1p1p4/3P1N2/5P2/6K1 b - - 1 40`

```
8  k . . . . . . .
7  . Q . . . . . .
6  p . . . . . p .
5  P . N . . . . .
4  . p . p . . . .
3  . . . P . N . .
2  . . . . . P . .
1  . . . . . . K .
   a b c d e f g h
```
