import chess
from chessboard import display
import numpy
import chess.svg

pieceValues = {
    'p': -100,
    'n': -300,
    'b': -300,
    'r': -500,
    'q': -900,
    'P': 100,
    'N': 300,
    'B': 300,
    'R': 500,
    'Q': 900
}

def calculateBoardMaterial(board: chess.Board):
    pieces = board.board_fen()
    advantage = 0
    for piece in pieces:
        advantage += pieceValues.get(piece, 0)
    
    return advantage

def evaluate(board: chess.Board):
    return calculateBoardMaterial(board)

def main():
    board = chess.Board("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")
    game_board = display.start()
    while True:
        display.check_for_quit()
        display.update(board.fen(), game_board)
        
    # print("Advantage: " + str(evaluate(board)))
    
if __name__ == "__main__":
    main()