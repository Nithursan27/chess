import minimax
import kmeans
import math
import statistics
from chessboard import display
import chess
import numpy as np
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
PLAY_GAME = True #Set True to emulate game against adversary
GAME_COUNT = 1 #Number of games to play against adversary
CURRENT_OPPONENT = STOCKFISH
DEPTH = 6
KMEANS_TURN = chess.WHITE

CHECK_RESULTS = False #Set True to check results of pgn file
RESULTS_PATH = "3000-4000_pgn,12000_samples,12_clusters,depth_6,mamopoccks,stockfish.pgn"

def get_results():
    pgn = open(RESULTS_PATH)
    opening_features = []
    midgame_features = []
    endgame_features = []
    wins = 0
    losses = 0
    draws = 0
    for i in range(30):
        game = chess.pgn.read_game(pgn)
        move_count = len(list(game.mainline_moves()))

        if kmeans.convert_outcome(game.headers["Result"]) == 'White':
            wins += 1
        if kmeans.convert_outcome(game.headers["Result"]) == 'Black':
            losses += 1
        if kmeans.convert_outcome(game.headers["Result"]) == 'Draw':
            draws += 1

        if move_count > 30:
            opening_count = random.randint(1,10)
            midgame_count = math.floor((move_count / 2))
            endgame_count = random.randint(move_count - 10, move_count - 1)
        else:
            opening_count = random.randint(1, 5)
            midgame_count = math.floor((move_count / 2))
            endgame_count = random.randint(move_count - 3, move_count - 1)
        
        board = game.board()
        count = 0
        for move in game.mainline_moves():
            board.push(move)
            count += 1
            if count == opening_count:
                opening_features.append(kmeans.extract_features(board))
            if count == midgame_count:
                midgame_features.append(kmeans.extract_features(board))
            if count == endgame_count:
                endgame_features.append(kmeans.extract_features(board))
        
    op_material = [i[0] for i in opening_features]
    op_positioning = [i[1] for i in opening_features]
    op_mobility = [i[2] for i in opening_features]
    op_centrecontrol = [i[3] for i in opening_features]
    op_kingsafety = [i[4] for i in opening_features]

    mid_material = [i[0] for i in midgame_features]
    mid_positioning = [i[1] for i in midgame_features]
    mid_mobility = [i[2] for i in midgame_features]
    mid_centrecontrol = [i[3] for i in midgame_features]
    mid_kingsafety = [i[4] for i in midgame_features]

    end_material = [i[0] for i in endgame_features]
    end_positioning = [i[1] for i in endgame_features]
    end_mobility = [i[2] for i in endgame_features]
    end_centrecontrol = [i[3] for i in endgame_features]
    end_kingsafety = [i[4] for i in endgame_features]

    print("W/L/D: " + str(wins) + "/" + str(losses) + "/" + str(draws) + "\n")

    print("Opening Results: \n")
    print("Material: " + str(statistics.fmean(op_material)))
    print("Positioning: " + str(statistics.fmean(op_positioning)))
    print("Mobility: " + str(statistics.fmean(op_mobility)))
    print("Centre Control: " + str(statistics.fmean(op_centrecontrol)))
    print("King Safety: " + str(statistics.fmean(op_kingsafety)))
    print("\n")

    print("Midgame Results: \n")
    print("Material: " + str(statistics.fmean(mid_material)))
    print("Positioning: " + str(statistics.fmean(mid_positioning)))
    print("Mobility: " + str(statistics.fmean(mid_mobility)))
    print("Centre Control: " + str(statistics.fmean(mid_centrecontrol)))
    print("King Safety: " + str(statistics.fmean(mid_kingsafety)))
    print("\n")

    print("Endgame Results: \n")
    print("Material: " + str(statistics.fmean(end_material)))
    print("Positioning: " + str(statistics.fmean(end_positioning)))
    print("Mobility: " + str(statistics.fmean(end_mobility)))
    print("Centre Control: " + str(statistics.fmean(end_centrecontrol)))
    print("King Safety: " + str(statistics.fmean(end_kingsafety)))


def test(setting, depth, turn):
    centroids, _ = kmeans.main()
    for i in range(GAME_COUNT):
        board = chess.Board()
        game = chess.pgn.Game()
        game.headers["Event"] = "Depth: " + str(depth)
        if KMEANS_TURN == chess.WHITE:
            game.headers["White"] = "K-Means"
            game.headers["Black"] = CURRENT_OPPONENT
        else:
            game.headers["Black"] = "K-Means"
            game.headers["White"] = CURRENT_OPPONENT
        
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_ENGINE_PATH)
        game_board = display.start()
        moves = []

        engine.configure({"Skill Level": 0})
        while not board.is_game_over():
            display.check_for_quit()

            if board.turn == turn:
                eval, result, pv = minimax.find_best_move(board, depth, centroids)
                if result == None:
                    result = list(board.legal_moves)[0]

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
        with open("3000-4000_pgn,3000_samples,12_clusters,depth_6,mamopoccks,stockfish.pgn", "a") as pgn_file:
            game.accept(chess.pgn.FileExporter(pgn_file))
        engine.quit()

if __name__ == "__main__":
    if CHECK_RESULTS:
        get_results()
    if PLAY_GAME:
        test(CURRENT_OPPONENT, DEPTH, KMEANS_TURN)
