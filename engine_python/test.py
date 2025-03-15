import minimax
import kmeans
from chessboard import display
import chess
import chess.pgn
import random
import chess.polyglot
import chess.engine
from time import sleep

STOCKFISH = "STOCKFISH"
USER = "USER"
RANDOM = "RANDOM"

STOCKFISH_ENGINE_PATH = r"C:\Users\Nithu\Desktop\chess\stockfish\stockfish-windows-x86-64-avx2.exe"

#K-Means Engine Variables
CURRENT_OPPONENT = RANDOM
DEPTH = 4
KMEANS_TURN = chess.WHITE

def test(setting, depth, turn):
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["Event"] = "Depth: " + str(depth)
    if KMEANS_TURN == chess.WHITE:
        game.headers["White"] = "K-Means"
        game.headers["Black"] = CURRENT_OPPONENT
    else:
        game.headers["Black"] = "K-Means"
        game.headers["WHITE"] = CURRENT_OPPONENT
    
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_ENGINE_PATH)
    game_board = display.start()
    centroids, _ = kmeans.main()
    moves = []

    engine.configure({"Skill Level": 0})
    while not board.is_game_over():
        display.check_for_quit()

        if board.turn == turn:
            eval, result, pv = minimax.find_best_move(board, depth, centroids)

        else:
            if setting == STOCKFISH:
                result = engine.play(board, chess.engine.Limit(time=0.1)).move

            elif setting == USER:
                result = chess.Move.from_uci(input("Enter move: "))

            else:
                result = random.choice(list(board.legal_moves))
        
        moves.append(result)
        board.push(result)
        display.update(board.fen(), game_board)
        sleep(1)
    game.headers["Result"] = chess.Board.result(board)
    node = game
    for move in moves:
        node = node.add_variation(move)
    with open("tests.pgn", "a") as pgn_file:
       game.accept(chess.pgn.FileExporter(pgn_file))
    engine.quit()

if __name__ == "__main__":
    test(CURRENT_OPPONENT, DEPTH, KMEANS_TURN)