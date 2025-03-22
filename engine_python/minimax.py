import chess
from chessboard import display
import chess.svg
import kmeans
import numpy as np

piece_values = {
    'p': -10,
    'n': -30,
    'b': -30,
    'r': -50,
    'q': -90,
    'P': 10,
    'N': 30,
    'B': 30,
    'R': 50,
    'Q': 90
}

pawn_table = [
 0,  0,  0,  0,  0,  0,  0,  0,
50, 50, 50, 50, 50, 50, 50, 50,
10, 10, 20, 30, 30, 20, 10, 10,
 5,  5, 10, 25, 25, 10,  5,  5,
 0,  0,  0, 20, 20,  0,  0,  0,
 5, -5,-10,  0,  0,-10, -5,  5,
 5, 10, 10,-20,-20, 10, 10,  5,
 0,  0,  0,  0,  0,  0,  0,  0
]

knight_table = [
-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  0,  0,  0,-20,-40,
-30,  0, 10, 15, 15, 10,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 10, 15, 15, 10,  5,-30,
-40,-20,  0,  5,  5,  0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50
]

bishop_table = [
-20,-10,-10,-10,-10,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0, 10, 10, 10, 10,  0,-10,
-10, 10, 10, 10, 10, 10, 10,-10,
-10,  5,  0,  0,  0,  0,  5,-10,
-20,-10,-10,-10,-10,-10,-10,-20
]

rook_table = [
  0,  0,  0,  0,  0,  0,  0,  0,
  5, 10, 10, 10, 10, 10, 10,  5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  0,  0,  0,  5,  5,  0,  0,  0
]

queen_table = [
-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5,  5,  5,  5,  0,-10,
 -5,  0,  5,  5,  5,  5,  0, -5,
  0,  0,  5,  5,  5,  5,  0, -5,
-10,  5,  5,  5,  5,  5,  0,-10,
-10,  0,  5,  0,  0,  0,  0,-10,
-20,-10,-10, -5, -5,-10,-10,-20
]

king_table = [
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-20,-30,-30,-40,-40,-30,-30,-20,
-10,-20,-20,-20,-20,-20,-20,-10,
 20, 20,  0,  0,  0,  0, 20, 20,
 20, 30, 10,  0,  0, 10, 30, 20
]

def calculate_board_material(board: chess.Board):
    pieces = board.board_fen()
    advantage = 0
    for piece in pieces:
        advantage += piece_values.get(piece, 0)
    
    return advantage

def calculate_PST(board: chess.Board):
    eval = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            match piece.piece_type:
                case chess.PAWN:
                    table = pawn_table
                case chess.BISHOP:
                    table = bishop_table
                case chess.KNIGHT:
                    table = knight_table
                case chess.ROOK:
                    table = rook_table
                case chess.QUEEN:
                    table = queen_table
                case chess.KING:
                    table = king_table
                case _:
                    continue
            if piece.color == chess.BLACK:
                square = chess.square(chess.square_file(square), 7 - chess.square_rank(square))
            
            if piece.color == chess.WHITE:
                eval += table[square] 
            else:
                eval += -table[square]
        
    return eval 

def calculate_mobility(board: chess.Board):
    if board.turn == chess.WHITE:
        white_moves = len(list(board.legal_moves))
        board.push(list(board.legal_moves)[0])
        black_moves = len(list(board.legal_moves))
        board.pop()
    else:
        black_moves = len(list(board.legal_moves))
        board.push(list(board.legal_moves)[0])
        white_moves = len(list(board.legal_moves))
        board.pop()

    return white_moves - black_moves

def calculate_centre_control(board: chess.Board):
    centre_control = 0
    centre_squares = [chess.square(3, 3), chess.square(3, 4), chess.square(4, 3), chess.square(4, 4)]
    for square in centre_squares:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                centre_control += 0.5
            else:
                centre_control -= 0.5
    return centre_control

def calculate_king_safety(board: chess.Board):
    king_safety = 0
    king_moves = [-1, 1, -8, 8, -9, 9, -7, 7]
    white_king_square = board.king(chess.WHITE)
    black_king_square = board.king(chess.BLACK)
    for move in king_moves:
        neighbour_square = white_king_square + move 
        if 0 <= neighbour_square <= 63:
            if board.is_attacked_by(chess.BLACK, neighbour_square):
                king_safety -= 1
    for move in king_moves:
        neighbour_square = black_king_square + move 
        if 0 <= neighbour_square <= 63:
            if board.is_attacked_by(chess.WHITE, neighbour_square):
                king_safety += 1

    return king_safety

def evaluate(board: chess.Board, centroids):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return float('-inf')
        return float('inf')
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        return len(centroids) / 2

    eval = kmeans.predict(kmeans.extract_prediction_data(board), centroids)

    return eval

def order_moves(board: chess.Board):
    capture_moves = []
    non_capture_moves = []
    for move in board.legal_moves:
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                captured_value = piece_values.get(captured_piece.piece_type, float('inf'))
                capture_moves.append((move, captured_value))
        else:
            non_capture_moves.append(move)
    capture_moves.sort(key=lambda x: x[1])
    sorted_capture_moves = [move[0] for move in capture_moves]
    return sorted_capture_moves + non_capture_moves
    
def minimax(board: chess.Board, depth: int, alpha: int, beta: int, is_max: bool, centroids):
    if (depth == 0) or board.is_game_over():
        return evaluate(board, centroids), None, []
    
    moves = order_moves(board)
    best_move = None
    best_PV = []
    
    if(is_max):
        max_eval = float('-inf')
        for move in moves:
            board.push(move)
            eval, _, pv = minimax(board, depth - 1, alpha, beta, False, centroids)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
                best_PV = [move] + pv
            alpha = max(alpha, eval)
            if (beta <= alpha):
                break
        
        return max_eval, best_move, best_PV
    
    else:
        min_eval = float('inf')
        for move in moves:
            board.push(move)
            eval, _, pv = minimax(board, depth - 1, alpha, beta, True, centroids)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
                best_PV = [move] + pv
            beta = min(beta, eval)
            if (beta <= alpha):
                break
        
        return min_eval, best_move, best_PV

def find_best_move(board, depth, centroids):
    is_max = board.turn == chess.WHITE
    eval, best_move, pv = minimax(board, depth, float('-inf'), float('inf'), is_max, centroids)
    return eval, best_move, pv

def main():
    board = chess.Board("rnb2rk1/ppp1qppp/3p4/8/2B5/6Q1/PPP1PPPP/RNB1K1NR w KQ - 0 1")
    game_board = display.start()
    print("Material: " + str(calculate_board_material(board)))
    print("PST: " + str(calculate_PST(board)))
    print("Mobility: " + str(calculate_mobility(board)))
    print("Centre Control: " + str(calculate_centre_control(board)))
    print("King Safety: " + str(calculate_king_safety(board)))

    # centroids, _ = kmeans.main()

    # eval, result, pv = find_best_move(board, 6, centroids)
    # print("Eval: " + str(eval))
    # print (pv)

    while True:
        display.check_for_quit()
        display.update(board.fen(), game_board)
    
if __name__ == "__main__":
    main()