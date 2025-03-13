import minimax
import kmeans
from chessboard import display
import chess
import random
import chess.polyglot
import chess.engine
from time import sleep

STOCKFISH = 1
USER = 2
RANDOM = 3

STOCKFISH_ENGINE_PATH = r"C:\Users\Nithu\Desktop\chess\stockfish\stockfish-windows-x86-64-avx2.exe"

CURRENT = RANDOM

def test(setting, depth = 4):
    board = chess.Board()

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_ENGINE_PATH)
    game_board = display.start()
    centroids, _ = kmeans.main()

    engine.configure({"Skill Level": 0})

    if setting == 1:
        while True:
            display.check_for_quit()

            if board.turn == chess.WHITE:
                eval, best_move, pv = minimax.find_best_move(board, depth)
                board.push(best_move)

            else:
                result = engine.play(board, chess.engine.Limit(time=0.1))
                board.push(result.move)

            display.update(board.fen(), game_board)
            sleep(1)
    elif setting == 2:
        while not board.is_game_over():
            display.check_for_quit()

            if board.turn == chess.WHITE:
                eval, best_move, pv = minimax.find_best_move(board, depth, centroids)
                board.push(best_move)

            else:
                result = input("Enter move: ")
                board.push(chess.Move.from_uci(result))

            display.update(board.fen(), game_board)
            sleep(1)
    else:
        while not board.is_game_over():
            display.check_for_quit()

            if board.turn == chess.WHITE:
                eval, best_move, pv = minimax.find_best_move(board, depth, centroids)
                board.push(best_move)

            else:
                result = random.choice(list(board.legal_moves))
                board.push(result)

            display.update(board.fen(), game_board)
            sleep(1)


    engine.quit()

if __name__ == "__main__":
    test(CURRENT)