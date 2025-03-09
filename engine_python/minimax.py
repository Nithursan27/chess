import chess
from chessboard import display
import chess.svg
import kmeans
import numpy as np

pieceValues = {
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

pawnTable = [
0,   0,   0,   0,   0,   0,   0,   0,
30,  30,  30,  40,  40,  30,  30,  30,
20,  20,  20,  30,  30,  30,  20,  20,
10,  10,  15,  25,  25,  15,  10,  10,
5,   5,   5,  20,  20,   5,   5,   5,
5,   0,   0,   5,   5,   0,   0,   5,
5,   5,   5, -10, -10,   5,   5,   5,
0,   0,   0,   0,   0,   0,   0,   0
]

knightTable = [
-5,  -5, -5, -5, -5, -5,  -5, -5,
-5,   0,  0, 10, 10,  0,   0, -5,
-5,   5, 10, 10, 10, 10,   5, -5,
-5,   5, 10, 15, 15, 10,   5, -5,
-5,   5, 10, 15, 15, 10,   5, -5,
-5,   5, 10, 10, 10, 10,   5, -5,
-5,   0,  0,  5,  5,  0,   0, -5,
-5, -10, -5, -5, -5, -5, -10, -5
]

bishopTable = [
0,   0,   0,   0,   0,   0,   0,   0,
0,   0,   0,   0,   0,   0,   0,   0,
0,   0,   0,   0,   0,   0,   0,   0,
0,  10,   0,   0,   0,   0,  10,   0,
5,   0,  10,   0,   0,  10,   0,   5,
0,  10,   0,  10,  10,   0,  10,   0,
0,  10,   0,  10,  10,   0,  10,   0,
0,   0, -10,   0,   0, -10,   0,   0
]

rookTable = [
10,  10,  10,  10,  10,  10,  10,  10,
10,  10,  10,  10,  10,  10,  10,  10,
0,   0,   0,   0,   0,   0,   0,   0,
0,   0,   0,   0,   0,   0,   0,   0,
0,   0,   0,   0,   0,   0,   0,   0,
0,   0,   0,   0,   0,   0,   0,   0,
0,   0,   0,  10,  10,   0,   0,   0,
0,   0,   0,  10,  10,   5,   0,   0
]

queenTable = [
-20, -10, -10, -5, -5, -10, -10, -20,
-10,   0,   0,  0,  0,   0,   0, -10,
-10,   0,   5,  5,  5,   5,   0, -10,
-5,   0,   5,  5,  5,   5,   0,  -5,
-5,   0,   5,  5,  5,   5,   0,  -5,
-10,   5,   5,  5,  5,   5,   0, -10,
-10,   0,   5,  0,  0,   0,   0, -10,
-20, -10, -10,  0,  0, -10, -10, -20
]

kingTable = [
0, 0,  0,  0,   0,  0,  0, 0,
0, 0,  0,  0,   0,  0,  0, 0,
0, 0,  0,  0,   0,  0,  0, 0,
0, 0,  0,  0,   0,  0,  0, 0,
0, 0,  0,  0,   0,  0,  0, 0,
0, 0,  0,  0,   0,  0,  0, 0,
0, 0,  0, -5,  -5, -5,  0, 0,
0, 0, 10, -5,  -5, -5, 10, 0
]

def calculateBoardMaterial(board: chess.Board):
    pieces = board.board_fen()
    advantage = 0
    for piece in pieces:
        advantage += pieceValues.get(piece, 0)
    
    return advantage

def calculatePST(board: chess.Board):
    eval = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            match piece.piece_type:
                case chess.PAWN:
                    table = pawnTable
                case chess.BISHOP:
                    table = bishopTable
                case chess.KNIGHT:
                    table = knightTable
                case chess.ROOK:
                    table = rookTable
                case chess.QUEEN:
                    table = queenTable
                case chess.KING:
                    table = kingTable
                case _:
                    continue
            if piece.color == chess.BLACK:
                square = chess.square(chess.square_file(square), 7 - chess.square_rank(square))
            
            if piece.color == chess.WHITE:
                eval += table[square] 
            else:
                eval += -table[square]
        
    return eval

def calculateCentreControl(board: chess.Board):
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

def evaluate(board: chess.Board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return float('-inf')
        return float('inf')
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
        return 0

    #Add endgame check
    game_phase_factor = 1.5

    material_eval = calculateBoardMaterial(board) * game_phase_factor
    pst_eval = calculatePST(board) * 0.5  
    centre_control_eval = calculateCentreControl(board) * game_phase_factor

    eval = material_eval + pst_eval + centre_control_eval

    return eval

def piece_hanging(board: chess.Board, move: chess.Move):
    moving_piece = board.piece_at(move.from_square)
    board.push(move)
    is_hanging = not board.is_attacked_by(moving_piece.color, move.to_square)
    board.pop()
    return is_hanging

def order_moves(board: chess.Board):
    captureMoves = []
    nonCaptureMoves = []
    for move in board.legal_moves:
        if board.is_capture(move):
            captureMoves.append(move)
        else:
            nonCaptureMoves.append(move)
    return captureMoves + nonCaptureMoves

def should_prune(board, move, centroids, isWhite):
    board.push(move)
    index = kmeans.predict(kmeans.extract_data(board), centroids)
    board.pop()
    white_adv = np.argmax(centroids[:, 0])
    black_adv = np.argmin(centroids[:, 0])
    if isWhite and index == black_adv:
        return True
    elif not isWhite and index == white_adv:
        return True
    return False
    
def minimax(board: chess.Board, depth: int, alpha: int, beta: int, isMax: bool, centroids):
    if (depth == 0) or board.is_game_over():
        return (evaluate(board)), None, []
    
    moves = order_moves(board)
    bestMove = None
    bestPV = []
    
    if(isMax):
        maxEval = float('-inf')
        for move in moves:
            # if should_prune(board, move, centroids, True):
            #     print("Pruned white")
            #     continue
            board.push(move)
            eval, _, pv = minimax(board, depth - 1, alpha, beta, False, centroids)
            board.pop()
            if eval > maxEval:
                maxEval = eval
                bestMove = move
                bestPV = [move] + pv
            alpha = max(alpha, eval)
            if (beta <= alpha):
                break
        
        return maxEval, bestMove, bestPV
    
    else:
        minEval = float('inf')
        for move in moves:
            # if should_prune(board, move, centroids, False):
            #     print("Pruned black")
            #     continue
            board.push(move)
            eval, _, pv = minimax(board, depth - 1, alpha, beta, True, centroids)
            board.pop()
            if eval < minEval:
                minEval = eval
                bestMove = move
                bestPV = [move] + pv
            beta = min(beta, eval)
            if (beta <= alpha):
                break
        
        return minEval, bestMove, bestPV

def find_best_move(board, depth, centroids):
    isMax = board.turn == chess.WHITE
    eval, bestMove, pv = minimax(board, depth, float('-inf'), float('inf'), isMax, centroids)
    return eval, bestMove, pv

def main():
    board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/QBQQKQBQ w kq - 0 1")
    # game_board = display.start()
    # print("Before Advantage: " + str(evaluate(board)))
    # eval, bestMove, pv = find_best_move(board, 4)
    # print("New advantage: " + str(eval) + " ", [move.uci() for move in pv])
    # board.push(bestMove)
    # while True:
    #     display.check_for_quit()
    #     display.update(board.fen(), game_board)
    centroids, _ = kmeans.main()
    print(should_prune(board, chess.Move.from_uci("e2e3"), centroids, True))
        
    
    
if __name__ == "__main__":
    main()