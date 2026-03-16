"""Comprehensive tests for the cozy-chess Python wrapper."""
import copy
import pytest

import cozy_chess


# ═══════════════════════════════════════════════════════════════════════════
# Enum Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestColor:
    def test_variants(self):
        assert cozy_chess.Color.White != cozy_chess.Color.Black

    def test_invert(self):
        assert ~cozy_chess.Color.White == cozy_chess.Color.Black
        assert ~cozy_chess.Color.Black == cozy_chess.Color.White

    def test_str(self):
        # Rust Display format uses lowercase single letter
        assert str(cozy_chess.Color.White) in ("w", "W", "White", "white")
        assert str(cozy_chess.Color.Black) in ("b", "B", "Black", "black")

    def test_hash(self):
        d = {cozy_chess.Color.White: "w", cozy_chess.Color.Black: "b"}
        assert d[cozy_chess.Color.White] == "w"


class TestPiece:
    def test_all_variants(self):
        pieces = [
            cozy_chess.Piece.Pawn, cozy_chess.Piece.Knight,
            cozy_chess.Piece.Bishop, cozy_chess.Piece.Rook,
            cozy_chess.Piece.Queen, cozy_chess.Piece.King,
        ]
        assert len(pieces) == cozy_chess.Piece.NUM
        assert len(set(pieces)) == 6

    def test_all(self):
        assert len(cozy_chess.Piece.ALL) == 6


class TestFile:
    def test_all_files(self):
        assert len(cozy_chess.File.ALL) == cozy_chess.File.NUM == 8

    def test_index(self):
        for i, f in enumerate(cozy_chess.File.ALL):
            assert int(f) == i


class TestRank:
    def test_all_ranks(self):
        assert len(cozy_chess.Rank.ALL) == cozy_chess.Rank.NUM == 8


class TestSquare:
    def test_num(self):
        assert cozy_chess.Square.NUM == 64
        assert len(cozy_chess.Square.ALL) == 64

    def test_new(self):
        sq = cozy_chess.Square.new(cozy_chess.File.A, cozy_chess.Rank.First)
        assert sq == cozy_chess.Square.A1

    def test_file_rank(self):
        sq = cozy_chess.Square.E4
        assert sq.file() == cozy_chess.File.E
        assert sq.rank() == cozy_chess.Rank.Fourth

    def test_from_str(self):
        sq = cozy_chess.Square.from_str("e4")
        assert sq == cozy_chess.Square.E4

    def test_flip(self):
        assert cozy_chess.Square.A1.flip_file() == cozy_chess.Square.H1
        assert cozy_chess.Square.A1.flip_rank() == cozy_chess.Square.A8

    def test_offset(self):
        sq = cozy_chess.Square.A1.offset(1, 2)
        assert sq == cozy_chess.Square.B3

    def test_try_offset_none(self):
        result = cozy_chess.Square.A1.try_offset(-1, 0)
        assert result is None

    def test_relative_to(self):
        assert cozy_chess.Square.A1.relative_to(cozy_chess.Color.White) == cozy_chess.Square.A1
        assert cozy_chess.Square.A1.relative_to(cozy_chess.Color.Black) == cozy_chess.Square.A8


class TestGameStatus:
    def test_variants(self):
        assert cozy_chess.GameStatus.Ongoing != cozy_chess.GameStatus.Won
        assert cozy_chess.GameStatus.Won != cozy_chess.GameStatus.Drawn


# ═══════════════════════════════════════════════════════════════════════════
# BitBoard Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestBitBoard:
    def test_empty(self):
        bb = cozy_chess.BitBoard.EMPTY
        assert len(bb) == 0
        assert bb.is_empty()
        assert not bb

    def test_full(self):
        bb = cozy_chess.BitBoard.FULL
        assert len(bb) == 64
        assert not bb.is_empty()
        assert bb

    def test_from_square(self):
        bb = cozy_chess.BitBoard.from_square(cozy_chess.Square.E4)
        assert len(bb) == 1
        assert bb.has(cozy_chess.Square.E4)
        assert not bb.has(cozy_chess.Square.E5)

    def test_bitwise_and(self):
        a = cozy_chess.BitBoard.from_rank(cozy_chess.Rank.First)
        b = cozy_chess.BitBoard.from_file(cozy_chess.File.A)
        result = a & b
        assert len(result) == 1
        assert result.has(cozy_chess.Square.A1)

    def test_bitwise_or(self):
        a = cozy_chess.BitBoard.from_square(cozy_chess.Square.A1)
        b = cozy_chess.BitBoard.from_square(cozy_chess.Square.H8)
        result = a | b
        assert len(result) == 2

    def test_bitwise_xor(self):
        a = cozy_chess.BitBoard.FULL
        b = cozy_chess.BitBoard.FULL
        result = a ^ b
        assert result == cozy_chess.BitBoard.EMPTY

    def test_invert(self):
        assert ~cozy_chess.BitBoard.EMPTY == cozy_chess.BitBoard.FULL
        assert ~cozy_chess.BitBoard.FULL == cozy_chess.BitBoard.EMPTY

    def test_sub(self):
        full = cozy_chess.BitBoard.FULL
        corners = cozy_chess.BitBoard.CORNERS
        result = full - corners
        assert len(result) == 60

    def test_contains(self):
        bb = cozy_chess.BitBoard.from_square(cozy_chess.Square.E4)
        assert cozy_chess.Square.E4 in bb
        assert cozy_chess.Square.A1 not in bb

    def test_iter(self):
        bb = cozy_chess.BitBoard.CORNERS
        squares = list(bb)
        assert len(squares) == 4
        assert cozy_chess.Square.A1 in squares
        assert cozy_chess.Square.H1 in squares
        assert cozy_chess.Square.A8 in squares
        assert cozy_chess.Square.H8 in squares

    def test_int(self):
        bb = cozy_chess.BitBoard.EMPTY
        assert int(bb) == 0
        bb = cozy_chess.BitBoard.FULL
        assert int(bb) == (1 << 64) - 1

    def test_from_value(self):
        bb = cozy_chess.BitBoard(0)
        assert bb == cozy_chess.BitBoard.EMPTY

    def test_flip_ranks(self):
        bb = cozy_chess.BitBoard.from_rank(cozy_chess.Rank.First)
        flipped = bb.flip_ranks()
        assert flipped == cozy_chess.BitBoard.from_rank(cozy_chess.Rank.Eighth)

    def test_is_subset(self):
        corners = cozy_chess.BitBoard.CORNERS
        full = cozy_chess.BitBoard.FULL
        assert corners.is_subset(full)
        assert not full.is_subset(corners)

    def test_is_superset(self):
        corners = cozy_chess.BitBoard.CORNERS
        full = cozy_chess.BitBoard.FULL
        assert full.is_superset(corners)

    def test_next_square(self):
        bb = cozy_chess.BitBoard.from_square(cozy_chess.Square.E4)
        assert bb.next_square() == cozy_chess.Square.E4
        assert cozy_chess.BitBoard.EMPTY.next_square() is None


# ═══════════════════════════════════════════════════════════════════════════
# Move Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestMove:
    def test_create(self):
        mv = cozy_chess.Move(cozy_chess.Square.E2, cozy_chess.Square.E4)
        assert mv.from_square == cozy_chess.Square.E2
        assert mv.to_square == cozy_chess.Square.E4
        assert mv.promotion is None

    def test_promotion(self):
        mv = cozy_chess.Move(
            cozy_chess.Square.E7, cozy_chess.Square.E8,
            cozy_chess.Piece.Queen,
        )
        assert mv.promotion == cozy_chess.Piece.Queen

    def test_from_str(self):
        mv = cozy_chess.Move.from_str("e2e4")
        assert str(mv) == "e2e4"
        assert mv.from_square == cozy_chess.Square.E2
        assert mv.to_square == cozy_chess.Square.E4

    def test_str_promotion(self):
        mv = cozy_chess.Move.from_str("e7e8q")
        assert str(mv) == "e7e8q"
        assert mv.promotion == cozy_chess.Piece.Queen

    def test_equality(self):
        a = cozy_chess.Move.from_str("e2e4")
        b = cozy_chess.Move(cozy_chess.Square.E2, cozy_chess.Square.E4)
        assert a == b

    def test_hash(self):
        mv = cozy_chess.Move.from_str("e2e4")
        d = {mv: True}
        assert d[cozy_chess.Move.from_str("e2e4")]


# ═══════════════════════════════════════════════════════════════════════════
# Board Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestBoard:
    def test_default(self):
        board = cozy_chess.Board()
        assert board.side_to_move() == cozy_chess.Color.White
        assert board.fullmove_number == 1
        assert board.halfmove_clock == 0

    def test_from_fen(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        board = cozy_chess.Board.from_fen(fen)
        assert board == cozy_chess.Board()

    def test_fen_roundtrip(self):
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        board = cozy_chess.Board.from_fen(fen)
        assert board.fen() == fen

    def test_startpos(self):
        assert cozy_chess.Board.startpos() == cozy_chess.Board()

    def test_pieces(self):
        board = cozy_chess.Board()
        pawns = board.pieces(cozy_chess.Piece.Pawn)
        assert len(pawns) == 16

    def test_colors(self):
        board = cozy_chess.Board()
        white = board.colors(cozy_chess.Color.White)
        assert len(white) == 16

    def test_colored_pieces(self):
        board = cozy_chess.Board()
        white_pawns = board.colored_pieces(cozy_chess.Color.White, cozy_chess.Piece.Pawn)
        assert len(white_pawns) == 8

    def test_occupied(self):
        board = cozy_chess.Board()
        assert len(board.occupied()) == 32

    def test_piece_on(self):
        board = cozy_chess.Board()
        assert board.piece_on(cozy_chess.Square.E1) == cozy_chess.Piece.King
        assert board.piece_on(cozy_chess.Square.E4) is None

    def test_color_on(self):
        board = cozy_chess.Board()
        assert board.color_on(cozy_chess.Square.E1) == cozy_chess.Color.White
        assert board.color_on(cozy_chess.Square.E8) == cozy_chess.Color.Black

    def test_king(self):
        board = cozy_chess.Board()
        assert board.king(cozy_chess.Color.White) == cozy_chess.Square.E1
        assert board.king(cozy_chess.Color.Black) == cozy_chess.Square.E8

    def test_castle_rights(self):
        board = cozy_chess.Board()
        rights = board.castle_rights(cozy_chess.Color.White)
        assert rights.short == cozy_chess.File.H
        assert rights.long == cozy_chess.File.A

    def test_generate_moves_startpos(self):
        board = cozy_chess.Board()
        moves = board.generate_moves()
        assert len(moves) == 20

    def test_play_move(self):
        board = cozy_chess.Board()
        mv = cozy_chess.Move.from_str("e2e4")
        board.play(mv)
        assert board.side_to_move() == cozy_chess.Color.Black
        assert board.piece_on(cozy_chess.Square.E4) == cozy_chess.Piece.Pawn
        assert board.piece_on(cozy_chess.Square.E2) is None

    def test_try_play(self):
        board = cozy_chess.Board()
        mv = cozy_chess.Move.from_str("e2e4")
        assert board.try_play(mv) is True
        # Board has been modified by try_play
        assert board.side_to_move() == cozy_chess.Color.Black

    def test_illegal_move(self):
        board = cozy_chess.Board()
        mv = cozy_chess.Move.from_str("e1e8")
        with pytest.raises(ValueError):
            board.play(mv)

    def test_is_legal(self):
        board = cozy_chess.Board()
        assert board.is_legal(cozy_chess.Move.from_str("e2e4"))
        assert not board.is_legal(cozy_chess.Move.from_str("e1e8"))

    def test_checkmate(self):
        """Scholar's mate."""
        board = cozy_chess.Board()
        moves = ["e2e4", "e7e5", "d1h5", "b8c6", "f1c4", "g8f6", "h5f7"]
        for m in moves:
            board.play(cozy_chess.Move.from_str(m))
        assert board.status() == cozy_chess.GameStatus.Won
        # Loser is the side to move
        assert board.side_to_move() == cozy_chess.Color.Black

    def test_status_ongoing(self):
        board = cozy_chess.Board()
        assert board.status() == cozy_chess.GameStatus.Ongoing

    def test_en_passant(self):
        board = cozy_chess.Board()
        assert board.en_passant() is None
        board.play(cozy_chess.Move.from_str("e2e4"))
        assert board.en_passant() == cozy_chess.File.E

    def test_hash(self):
        a = cozy_chess.Board()
        b = cozy_chess.Board()
        assert a.hash() == b.hash()

    def test_null_move(self):
        board = cozy_chess.Board()
        nm = board.null_move()
        assert nm is not None
        assert nm.side_to_move() == cozy_chess.Color.Black

    def test_same_position(self):
        a = cozy_chess.Board()
        b = cozy_chess.Board()
        assert a.same_position(b)

    def test_generate_moves_for(self):
        board = cozy_chess.Board()
        knights = board.pieces(cozy_chess.Piece.Knight)
        knight_moves = board.generate_moves_for(knights)
        assert len(knight_moves) == 4

    def test_kiwipete_moves(self):
        fen = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
        board = cozy_chess.Board.from_fen(fen)
        moves = board.generate_moves()
        assert len(moves) == 48

    def test_copy(self):
        board = cozy_chess.Board()
        board2 = copy.copy(board)
        board.play(cozy_chess.Move.from_str("e2e4"))
        assert board != board2  # copy is independent

    def test_deepcopy(self):
        board = cozy_chess.Board()
        board2 = copy.deepcopy(board)
        board.play(cozy_chess.Move.from_str("e2e4"))
        assert board != board2

    def test_chess960(self):
        board = cozy_chess.Board.chess960_startpos(518)
        assert board == cozy_chess.Board()

    def test_pinned(self):
        board = cozy_chess.Board()
        pinned = board.pinned()
        assert pinned.is_empty()

    def test_checkers(self):
        board = cozy_chess.Board()
        assert board.checkers().is_empty()

    def test_str_returns_fen(self):
        board = cozy_chess.Board()
        expected = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        assert str(board) == expected

    def test_pretty(self):
        board = cozy_chess.Board()
        pretty = board.pretty()
        assert "K" in pretty  # White king
        assert "k" in pretty  # Black king

    def test_set_halfmove_clock(self):
        board = cozy_chess.Board()
        board.set_halfmove_clock(50)
        assert board.halfmove_clock == 50

    def test_set_fullmove_number(self):
        board = cozy_chess.Board()
        board.set_fullmove_number(10)
        assert board.fullmove_number == 10

    def test_generate_piece_moves(self):
        board = cozy_chess.Board()
        piece_moves = board.generate_piece_moves()
        total = sum(len(pm) for pm in piece_moves)
        assert total == 20


# ═══════════════════════════════════════════════════════════════════════════
# PieceMoves Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestPieceMoves:
    def test_iteration(self):
        board = cozy_chess.Board()
        piece_moves_list = board.generate_piece_moves()
        for pm in piece_moves_list:
            assert len(pm) > 0
            for mv in pm:
                assert isinstance(mv, cozy_chess.Move)

    def test_properties(self):
        board = cozy_chess.Board()
        piece_moves_list = board.generate_piece_moves()
        for pm in piece_moves_list:
            assert isinstance(pm.piece, cozy_chess.Piece)
            assert isinstance(pm.from_square, cozy_chess.Square)
            assert isinstance(pm.to, cozy_chess.BitBoard)


# ═══════════════════════════════════════════════════════════════════════════
# CastleRights Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCastleRights:
    def test_default_rights(self):
        board = cozy_chess.Board()
        rights = board.castle_rights(cozy_chess.Color.White)
        assert rights.short == cozy_chess.File.H
        assert rights.long == cozy_chess.File.A
        assert rights.has_short()
        assert rights.has_long()

    def test_lost_rights(self):
        board = cozy_chess.Board()
        board.play(cozy_chess.Move.from_str("e2e4"))
        board.play(cozy_chess.Move.from_str("e7e5"))
        board.play(cozy_chess.Move.from_str("e1e2"))  # King moves, loses rights
        rights = board.castle_rights(cozy_chess.Color.White)
        assert rights.short is None
        assert rights.long is None


# ═══════════════════════════════════════════════════════════════════════════
# BoardBuilder Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestBoardBuilder:
    def test_default_builds_startpos(self):
        builder = cozy_chess.BoardBuilder()
        board = builder.build()
        assert board == cozy_chess.Board()

    def test_from_board(self):
        board = cozy_chess.Board()
        builder = cozy_chess.BoardBuilder.from_board(board)
        rebuilt = builder.build()
        assert rebuilt == board

    def test_empty(self):
        builder = cozy_chess.BoardBuilder.empty()
        assert builder.piece_on(cozy_chess.Square.A1) is None

    def test_set_and_clear_piece(self):
        builder = cozy_chess.BoardBuilder.empty()
        builder.set_piece(cozy_chess.Square.E1, cozy_chess.Piece.King, cozy_chess.Color.White)
        assert builder.piece_on(cozy_chess.Square.E1) == cozy_chess.Piece.King
        assert builder.color_on(cozy_chess.Square.E1) == cozy_chess.Color.White
        builder.clear_piece(cozy_chess.Square.E1)
        assert builder.piece_on(cozy_chess.Square.E1) is None

    def test_side_to_move(self):
        builder = cozy_chess.BoardBuilder()
        assert builder.side_to_move == cozy_chess.Color.White
        builder.set_side_to_move(cozy_chess.Color.Black)
        assert builder.side_to_move == cozy_chess.Color.Black


# ═══════════════════════════════════════════════════════════════════════════
# Free Functions Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestFunctions:
    def test_king_moves(self):
        moves = cozy_chess.get_king_moves(cozy_chess.Square.E4)
        assert len(moves) == 8

    def test_king_moves_corner(self):
        moves = cozy_chess.get_king_moves(cozy_chess.Square.A1)
        assert len(moves) == 3

    def test_knight_moves(self):
        moves = cozy_chess.get_knight_moves(cozy_chess.Square.E4)
        assert len(moves) == 8

    def test_knight_moves_corner(self):
        moves = cozy_chess.get_knight_moves(cozy_chess.Square.A1)
        assert len(moves) == 2

    def test_rook_moves_empty(self):
        moves = cozy_chess.get_rook_moves(cozy_chess.Square.E4, cozy_chess.BitBoard.EMPTY)
        assert len(moves) == 14

    def test_bishop_moves_empty(self):
        moves = cozy_chess.get_bishop_moves(cozy_chess.Square.E4, cozy_chess.BitBoard.EMPTY)
        assert len(moves) == 13

    def test_rook_rays(self):
        rays = cozy_chess.get_rook_rays(cozy_chess.Square.E4)
        assert len(rays) == 14

    def test_bishop_rays(self):
        rays = cozy_chess.get_bishop_rays(cozy_chess.Square.E4)
        assert len(rays) == 13

    def test_pawn_attacks(self):
        attacks = cozy_chess.get_pawn_attacks(cozy_chess.Square.E4, cozy_chess.Color.White)
        assert len(attacks) == 2
        assert attacks.has(cozy_chess.Square.D5)
        assert attacks.has(cozy_chess.Square.F5)

    def test_pawn_quiets(self):
        # From starting position, E2 pawn can move to E3 and E4
        quiets = cozy_chess.get_pawn_quiets(
            cozy_chess.Square.E2,
            cozy_chess.Color.White,
            cozy_chess.BitBoard.EMPTY,
        )
        assert len(quiets) == 2

    def test_between_rays(self):
        between = cozy_chess.get_between_rays(cozy_chess.Square.A1, cozy_chess.Square.H8)
        # Should have the diagonal squares between
        assert len(between) > 0

    def test_line_rays(self):
        line = cozy_chess.get_line_rays(cozy_chess.Square.A1, cozy_chess.Square.H8)
        assert len(line) > 0
