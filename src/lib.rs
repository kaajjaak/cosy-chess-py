#![allow(non_snake_case)]

use pyo3::prelude::*;

pub mod enums;
pub mod bitboard;
pub mod chess_move;
pub mod piece_moves;
pub mod castle_rights;
pub mod board;
pub mod board_builder;
pub mod functions;

#[pymodule]
fn cozy_chess(m: &Bound<'_, PyModule>) -> PyResult<()> {
    enums::register(m)?;
    bitboard::register(m)?;
    chess_move::register(m)?;
    piece_moves::register(m)?;
    castle_rights::register(m)?;
    board::register(m)?;
    board_builder::register(m)?;
    functions::register(m)?;
    Ok(())
}
