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

def evaluate(board: chess.Board, centroids):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return float('-inf')
        return float('inf')
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        return len(centroids) / 2

    eval = kmeans.predict(kmeans.extract_prediction_data(board), centroids)

    return eval

def piece_hanging(board: chess.Board, move: chess.Move):
    moving_piece = board.piece_at(move.from_square)
    board.push(move)
    is_hanging = not board.is_attacked_by(moving_piece.color, move.to_square)
    board.pop()
    return is_hanging

def order_moves(board: chess.Board):
    capture_moves = []
    non_capture_moves = []
    for move in board.legal_moves:
        if board.is_capture(move):
            capture_moves.append(move)
        else:
            non_capture_moves.append(move)
    return capture_moves + non_capture_moves

def should_prune(board, move, centroids, is_white):
    board.push(move)
    index = kmeans.predict(kmeans.extract_prediction_data(board), centroids)
    board.pop()
    white_adv = np.argmax(centroids[:, 0])
    black_adv = np.argmin(centroids[:, 0])
    if is_white and index == black_adv:
        return True
    elif not is_white and index == white_adv:
        return True
    return False
    
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
    board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/QBQQKQBQ w kq - 0 1")
    # game_board = display.start()
    # print("Before Advantage: " + str(evaluate(board)))
    # eval, best_move, pv = find_best_move(board, 4)
    # print("New advantage: " + str(eval) + " ", [move.uci() for move in pv])
    # board.push(best_move)
    # while True:
    #     display.check_for_quit()
    #     display.update(board.fen(), game_board)
    centroids, _ = kmeans.main()
    print(should_prune(board, chess.Move.from_uci("e2e3"), centroids, True))
        
    
    
if __name__ == "__main__":
    main()