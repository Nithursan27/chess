import minimax
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs

import chess.pgn

def convert_outcome(outcome):
    match outcome:
        case '1-0':
            return 'White'
        case '0-1':
            return 'Black'
        case '1/2-1/2':
            return 'Draw'
        case _:
            return 'Error'

def initialise_data():
    pgn = open("data/2500-4000.pgn")
    evaluation_scores = []
    turn_counts = []
    outcomes = []
    i = 0
    while (i < 1):
        game = chess.pgn.read_game(pgn)
        if game is not None:
            board = game.board()
            turns = 0
            for move in game.mainline_moves():
                board.push(move)
                turns += 1
            evaluation = minimax.evaluate(board)
            outcome = convert_outcome(game.headers["Result"])
            evaluation_scores.append(evaluation)
            turn_counts.append(turns)
            outcomes.append(outcome)
        else:
            break
        i += 1
    x_data = np.array([evaluation_scores, turn_counts])
    y_data = np.array(outcomes)

    return (x_data, y_data)

def initialise_centroids(data, k):
    np.random.seed(0)
    random_indices = np.random.permutation(data.shape[0])


def main():
    data = initialise_data()
    x_data = data[0]
    # x_data, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0)
    y_data = data[1]
    print(data)
    fig = plt.figure(0)
    plt.grid(True)
    plt.scatter(x_data[:, 0],x_data[:, 1])
    plt.show()
    
if __name__ == "__main__":
    main()