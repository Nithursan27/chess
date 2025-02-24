import minimax
from chessboard import display
import chess
import chess.engine
from time import sleep

def test_against_stockfish(depth = 3):
    board = chess.Board()

    engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\Nithu\Desktop\chess\stockfish\stockfish-windows-x86-64-avx2.exe")
    game_board = display.start()

    engine.configure({"Skill Level": 0})

    while not board.is_game_over():
        display.check_for_quit()

        if board.turn == chess.WHITE:
            eval, best_move, pv = minimax.find_best_move(board, depth)
            board.push(best_move)

        else:
            result = engine.play(board, chess.engine.Limit(time=0.1))
            board.push(result.move)

        display.update(board.fen(), game_board)
        sleep(1)


    engine.quit()


if __name__ == "__main__":
    test_against_stockfish()