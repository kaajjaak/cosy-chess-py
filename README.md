# cozy-chess-py

[![CI](https://github.com/kaajjaak/cosy-chess-py/actions/workflows/CI.yml/badge.svg)](https://github.com/kaajjaak/cosy-chess-py/actions/workflows/CI.yml)
[![PyPI](https://img.shields.io/pypi/v/cozy-chess-py)](https://pypi.org/project/cozy-chess-py/)

Python bindings for [cozy-chess](https://github.com/analog-hors/cozy-chess) — a fast, strongly-typed Rust chess move generation library. Built with [PyO3](https://pyo3.rs) and [maturin](https://maturin.rs).

## Features

- Full chess & Chess960 / DFRC legal move generation
- Pythonic API with operator overloading, iteration, `__hash__`, `__copy__`, `__deepcopy__`
- Complete type stubs (`.pyi`) for IDE autocompletion and type checking
- Thin wrapper — performance stays close to the Rust core
- **No Rust required for end users** — prebuilt wheels for Windows, Linux, and macOS

## Installation

```bash
pip install cozy-chess-py
```

### Build from source

#### Requirements

- Python ≥ 3.8
- Rust toolchain ([rustup.rs](https://rustup.rs))
- [maturin](https://maturin.rs): `pip install maturin`

### Build from source

```bash
git clone https://github.com/kaajjaak/cosy-chess-py
cd cosy-chess-py

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

pip install maturin pytest
maturin develop --release
```

## Quick Start

```python
import cozy_chess as cc

# Starting position
board = cc.Board()
print(board.pretty())

# Generate legal moves
moves = board.generate_moves()
print(f"{len(moves)} moves in starting position")  # 20

# Play moves
board.play(cc.Move.from_str("e2e4"))
board.play(cc.Move.from_str("e7e5"))

# Or construct from a FEN string
board = cc.Board.from_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1")
print(f"{len(board.generate_moves())} moves in Kiwipete")  # 48
```

## API Reference

### Enums

| Class | Variants |
|-------|----------|
| `Color` | `White`, `Black` |
| `Piece` | `Pawn`, `Knight`, `Bishop`, `Rook`, `Queen`, `King` |
| `File` | `A`–`H` |
| `Rank` | `First`–`Eighth` |
| `Square` | `A1`–`H8` (all 64) |
| `GameStatus` | `Ongoing`, `Won`, `Drawn` |

All enum types support `==`, `hash()`, and can be used as dict keys.

```python
~cc.Color.White          # → Color.Black (invert)
cc.Square.E4.file()      # → File.E
cc.Square.E4.rank()      # → Rank.Fourth
cc.Square.E4.flip_rank() # → Square.E5
cc.Square.new(cc.File.E, cc.Rank.Fourth)  # → Square.E4
```

### `Board`

```python
# Constructors
board = cc.Board()                                  # starting position
board = cc.Board.from_fen("rnbqkbnr/... w KQkq - 0 1")
board = cc.Board.chess960_startpos(518)

# Queries
board.side_to_move()                  # → Color
board.piece_on(cc.Square.E1)          # → Optional[Piece]
board.color_on(cc.Square.E1)          # → Optional[Color]
board.king(cc.Color.White)            # → Square
board.occupied()                      # → BitBoard
board.pieces(cc.Piece.Pawn)           # → BitBoard
board.colors(cc.Color.White)          # → BitBoard
board.colored_pieces(cc.Color.White, cc.Piece.Pawn)  # → BitBoard
board.castle_rights(cc.Color.White)   # → CastleRights
board.en_passant()                    # → Optional[File]
board.checkers()                      # → BitBoard
board.pinned()                        # → BitBoard
board.hash()                          # → int (Zobrist)
board.status()                        # → GameStatus

# Gameplay
board.play(cc.Move.from_str("e2e4"))   # raises ValueError if illegal
board.try_play(mv)                     # → bool, modifies board
board.is_legal(mv)                     # → bool, does not modify
board.null_move()                      # → Optional[Board]
board.same_position(other)             # FIDE equivalence (threefold rep)

# Move generation — flat list
moves = board.generate_moves()                       # → list[Move]
moves = board.generate_moves_for(mask: BitBoard)     # subset of pieces

# Move generation — grouped by source piece
for pm in board.generate_piece_moves():
    print(pm.piece, pm.from_square, pm.to)   # pm.to is a BitBoard
    for mv in pm:
        ...

# FEN output
board.fen()          # standard FEN
board.shredder_fen() # Shredder FEN (Chess960)
board.pretty()       # ASCII board display
str(board)           # same as board.fen()
```

### `BitBoard`

```python
# Constants
cc.BitBoard.EMPTY; cc.BitBoard.FULL; cc.BitBoard.EDGES
cc.BitBoard.CORNERS; cc.BitBoard.DARK_SQUARES; cc.BitBoard.LIGHT_SQUARES

# Construction
bb = cc.BitBoard(0xFFFF)                    # from raw u64
bb = cc.BitBoard.from_square(cc.Square.E4)
bb = cc.BitBoard.from_file(cc.File.E)
bb = cc.BitBoard.from_rank(cc.Rank.Fourth)
bb = cc.BitBoard.from_squares([cc.Square.A1, cc.Square.H8])

# Operators
a & b;  a | b;  a ^ b;  a - b;  ~a

# Queries
len(bb)           # number of set squares
bool(bb)          # False if empty
sq in bb          # square membership
bb.has(sq)        # same as above
bb.next_square()  # → Optional[Square] (LSB)
list(bb)          # → list[Square]
int(bb)           # → raw u64 value

# Transformations
bb.flip_ranks(); bb.flip_files()
bb.is_subset(other); bb.is_superset(other); bb.is_disjoint(other)
```

### `Move`

```python
mv = cc.Move(cc.Square.E2, cc.Square.E4)
mv = cc.Move(cc.Square.E7, cc.Square.E8, cc.Piece.Queen)  # promotion
mv = cc.Move.from_str("e2e4")           # UCI format
mv = cc.Move.from_str("e7e8q")          # promotion

mv.from_square   # → Square
mv.to_square     # → Square
mv.promotion     # → Optional[Piece]
str(mv)          # → "e2e4" / "e7e8q"
```

### `BoardBuilder`

```python
builder = cc.BoardBuilder()              # default startpos
builder = cc.BoardBuilder.empty()        # empty board
builder = cc.BoardBuilder.from_board(board)

builder.set_piece(cc.Square.E1, cc.Piece.King, cc.Color.White)
builder.clear_piece(cc.Square.E1)
builder.set_side_to_move(cc.Color.Black)
builder.set_castle_rights(cc.Color.White, short=cc.File.H, long=cc.File.A)
builder.set_en_passant(cc.Square.E6)
builder.set_halfmove_clock(0)
builder.set_fullmove_number(1)
board = builder.build()                  # → Board (raises ValueError if invalid)
```

### Free Functions

Move tables for custom move generation:

```python
cc.get_king_moves(sq)                     # → BitBoard
cc.get_knight_moves(sq)                   # → BitBoard
cc.get_bishop_moves(sq, blockers)         # → BitBoard (sliding, with blockers)
cc.get_rook_moves(sq, blockers)           # → BitBoard (sliding, with blockers)
cc.get_bishop_rays(sq)                    # → BitBoard (unblocked rays)
cc.get_rook_rays(sq)                      # → BitBoard (unblocked rays)
cc.get_pawn_attacks(sq, color)            # → BitBoard
cc.get_pawn_quiets(sq, color, blockers)   # → BitBoard
cc.get_between_rays(sq_a, sq_b)           # → BitBoard (squares between)
cc.get_line_rays(sq_a, sq_b)              # → BitBoard (full line through both)
```

## Running Tests

```bash
python -m pytest tests/ -v
```

96 tests, all passing.

## Publishing a Release

Wheels are built and published automatically via GitHub Actions.

1. **Set up PyPI Trusted Publishing** (one-time):
   - Go to [pypi.org](https://pypi.org) → Your account → Publishing
   - Add a new trusted publisher: owner `kaajjaak`, repo `cosy-chess-py`, workflow `release.yml`

2. **Tag a release**:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

   GitHub Actions will automatically:
   - Build wheels for Windows, Linux (x86_64 + ARM64), and macOS (Intel + Apple Silicon)
   - Build for Python 3.8–3.13
   - Upload everything to PyPI

## License

MIT — see [LICENSE](LICENSE). This project wraps [cozy-chess](https://github.com/analog-hors/cozy-chess) which is also MIT licensed (Copyright © 2021 analog-hors).
