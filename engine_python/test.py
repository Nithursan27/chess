import minimax
from chessboard import display
import chess
import chess.polyglot
import chess.engine
from time import sleep



def test(stockfish, depth = 4):
    board = chess.Board()

    engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\Nithu\Desktop\chess\stockfish\stockfish-windows-x86-64-avx2.exe")
    game_board = display.start()

    engine.configure({"Skill Level": 0})
    checkBook = True

    if stockfish:
        while not board.is_game_over():
            display.check_for_quit()

            if board.turn == chess.WHITE:
                if checkBook:
                    with chess.polyglot.open_reader(r"C:\Users\Nithu\Desktop\chess\engine_python\data\baron30.bin") as reader:
                        if not list(reader.find_all(board)):
                            checkBook = False
                            eval, best_move, pv = minimax.find_best_move(board, depth)
                            board.push(best_move)

                        for entry in reader.find_all(board):
                            board.push(entry.move)
                else:
                    eval, best_move, pv = minimax.find_best_move(board, depth)
                    board.push(best_move)

            else:
                result = engine.play(board, chess.engine.Limit(time=0.1))
                board.push(result.move)

            display.update(board.fen(), game_board)
            sleep(1)
    else:
        while not board.is_game_over():
            display.check_for_quit()

            if board.turn == chess.WHITE:
                eval, best_move, pv = minimax.find_best_move(board, depth)
                board.push(best_move)

            else:
                result = input("Enter move: ")
                board.push(chess.Move.from_uci(result))

            display.update(board.fen(), game_board)
            sleep(1)


    engine.quit()

if __name__ == "__main__":
    test(True)