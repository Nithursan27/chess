import chess
from chessboard import display
import numpy
import chess.svg

pieceValues = {
    'p': -1,
    'n': -3,
    'b': -3,
    'r': -5,
    'q': -9,
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9
}

def calculateBoardMaterial(board: chess.Board):
    pieces = board.board_fen()
    advantage = 0
    for piece in pieces:
        advantage += pieceValues.get(piece, 0)
    
    return advantage

def evaluate(board: chess.Board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return float('-inf')
        return float('inf')
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
        return 0
    
    eval = calculateBoardMaterial(board)

    return eval

def minimax(board: chess.Board, depth: int, alpha: int, beta: int, isMax: bool):
    if (depth == 0) or board.is_game_over():
        return(evaluate(board)), None, []
    
    moves = list(board.legal_moves)
    bestMove = None
    bestPV = []
    
    if(isMax):
        maxEval = float('-inf')
        for move in moves:
            board.push(move)
            eval, _, pv = minimax(board, depth - 1, alpha, beta, False)
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
            board.push(move)
            eval, _, pv = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval < minEval:
                minEval = eval
                bestMove = move
                bestPV = [move] + pv
            beta = min(beta, eval)
            if (beta <= alpha):
                break
        
        return minEval, bestMove, bestPV

def find_best_move(board, depth):
    isMax = board.turn == chess.WHITE
    eval, bestMove, pv = minimax(board, depth, float('-inf'), float('inf'), isMax)
    return eval, bestMove, pv

def main():
    board = chess.Board("rnbqkbnr/pppppppp/8/1r1n4/2P5/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1")
    print(board)
    game_board = display.start()
    print("Before Advantage: " + str(evaluate(board)))
    print(board.legal_moves)
    eval, bestMove, pv = find_best_move(board, 3)
    print("New advantage: " + str(eval) + " ", [move.uci() for move in pv])
    board.push(bestMove)
    while True:
        display.check_for_quit()
        display.update(board.fen(), game_board)
        
    
    
if __name__ == "__main__":
    main()