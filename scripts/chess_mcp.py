from mcp.server.fastmcp import FastMCP
import chess

mcp = FastMCP("chess")

_board = chess.Board()

def _render() -> str:
    b = _board
    turn = "White" if b.turn == chess.WHITE else "Black"
    status = "normal"
    if b.is_checkmate():
        status = "CHECKMATE! Winner: %s" % ("Black" if b.turn == chess.WHITE else "White")
    elif b.is_stalemate():
        status = "STALEMATE (draw)"
    elif b.is_insufficient_material():
        status = "DRAW (insufficient material)"
    elif b.is_check():
        status = "CHECK"
    legal = ", ".join(b.san(m) for m in b.legal_moves)
    return ("%s\nTurn: %s | Status: %s\nFEN: %s\nLegal moves: %s" % (str(b), turn, status, b.fen(), legal))

@mcp.tool()
def new_game() -> str:
    """Start a new chess game. The user plays White (first), the AI plays Black. Returns the initial board."""
    global _board
    _board = chess.Board()
    return "New game. User=White, AI=Black.\n" + _render()

@mcp.tool()
def show_board() -> str:
    """Show the current chess board, whose turn it is, status, and all legal moves."""
    return _render()

@mcp.tool()
def make_move(move: str) -> str:
    """Play one move for the side whose turn it is. Accepts SAN (e4, Nf3, O-O, exd5, e8=Q) or UCI (e2e4).
    move: the chess move, e.g. 'e4' or 'e2e4'"""
    global _board
    if _board.is_game_over():
        return "Game over already.\n" + _render()
    mv = None
    try:
        mv = _board.parse_san(move)
    except Exception:
        mv = None
    if mv is None:
        try:
            mv = chess.Move.from_uci(move)
            if mv not in _board.legal_moves:
                mv = None
        except Exception:
            mv = None
    if mv is None:
        legal = ", ".join(_board.san(m) for m in _board.legal_moves)
        return "Illegal move: %s\nLegal moves: %s" % (move, legal)
    _board.push(mv)
    return _render()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.streamable_http_app(), host="127.0.0.1", port=18004)
