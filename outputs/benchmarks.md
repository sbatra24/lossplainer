# Benchmarks

Measured on this machine: Python 3.11.15, x86_64, single thread. Numbers are from one run of `python report.py bench`.

## Perft (legal move generator)

| position | depth | nodes | seconds |
|---|---|---|---|
| start position | 1 | 20 | 0.00 |
| start position | 2 | 400 | 0.00 |
| start position | 3 | 8,902 | 0.01 |
| start position | 4 | 197,281 | 0.37 |
| start position | 5 | 4,865,609 | 8.94 |
| Kiwipete | 1 | 48 | 0.00 |
| Kiwipete | 2 | 2,039 | 0.01 |
| Kiwipete | 3 | 97,862 | 0.20 |
| Kiwipete | 4 | 4,085,603 | 8.31 |

## Search speed with the trained network

Feature extraction builds 107 named features per leaf in pure Python, so the node rate is low. Quiescence nodes are included in the count; every search starts with an empty transposition table and an empty evaluation cache.

| position | depth | nodes | seconds | nodes/sec | score | principal variation |
|---|---|---|---|---|---|---|
| start position | 3 | 1,451 | 0.19 | 7,567 | +0.37 | 1. e4 d5 2. e5 |
| start position | 4 | 6,625 | 1.08 | 6,120 | +0.05 | 1. e4 d5 2. e5 Nc6 |
| start position | 5 | 32,708 | 4.66 | 7,020 | +0.36 | 1. e4 d5 2. e5 d4 3. Qf3 |
| Kiwipete | 3 | 36,801 | 6.88 | 5,349 | +0.35 | 1. dxe6 Qxe6 2. Bxa6 hxg2 |
| Kiwipete | 4 | 88,631 | 15.97 | 5,550 | +0.35 | 1. dxe6 Qxe6 2. Bxa6 hxg2 |
| Kiwipete | 5 | 386,452 | 53.76 | 7,188 | +0.14 | 1. dxe6 Qxe6 2. Bxa6 hxg2 3. Qxg2 Qxe5 |
| Italian middlegame | 3 | 2,659 | 0.31 | 8,680 | +0.19 | 8. cxd5 Bxc3+ 9. bxc3 Ne7 |
| Italian middlegame | 4 | 9,934 | 0.88 | 11,321 | +0.46 | 8. cxd5 Bxc3+ 9. bxc3 Qf6 10. dxc6 Qxc3+ 11. Nd2 bxc6 |
| Italian middlegame | 5 | 39,668 | 4.45 | 8,916 | +0.43 | 8. cxd5 Bxc3+ 9. bxc3 Ne7 10. e4 Bd7 |
| rook endgame | 3 | 1,326 | 0.09 | 15,287 | -2.07 | 20... b6 21. Rb1 Rxc3 |
| rook endgame | 4 | 6,092 | 0.51 | 12,035 | -2.25 | 20... a6 21. Rb1 b5 22. Rb3 |
| rook endgame | 5 | 37,455 | 2.76 | 13,577 | -2.05 | 20... b5 21. Nd2 b4 22. c4 a6 |
