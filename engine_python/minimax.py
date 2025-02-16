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
    return calculateBoardMaterial(board)

def minimax(board: chess.Board, depth: int, alpha: int, beta: int, isMax: bool):
    if (depth == 0) or board.is_game_over():
        return(evaluate(board))
    
    moves = list(board.legal_moves)
    
    if(isMax):
        maxEval = float('-inf')
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            maxEval = max(maxEval, eval)
            alpha = max(alpha, maxEval)
            if (beta <= alpha):
                break
        
        return maxEval
    
    else:
        minEval = float('inf')
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            minEval = min(minEval, eval)
            beta = min(beta, minEval)
            if (beta <= alpha):
                break
        
        return minEval


def main():
    board = chess.Board("rnbqkbnr/pppppppp/8/1r1n4/2P5/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    game_board = display.start()
    print("Before Advantage: " + str(evaluate(board)))
    print(board.legal_moves)
    print("New advantage:" + str(minimax(board, 1, float('-inf'), float('inf'), True)))
    while True:
        display.check_for_quit()
        display.update(board.fen(), game_board)
        
    
    
if __name__ == "__main__":
    main()