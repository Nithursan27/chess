import minimax
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

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
        
#Finish this method
def generate_position(board: chess.Board, moves):
        
    i = random.randint(1,20)
    for move in moves:
        if board.is_game_over():
            board.pop()
            break
        elif i <= 0:
            break
        board.push(move)
        i -= 1 
    return board

def extract_data(board: chess.Board):
    return np.array([minimax.evaluate(board), len(list(board.legal_moves))])

def initialise_data():
    pgn = open("data/3000-4000.pgn")
    evaluation_scores = []
    mobility_scores = []
    outcomes = []
    sample_count = 1000
    i = 0
    while (i < sample_count):
        game = chess.pgn.read_game(pgn)
        if game is not None:
            board = generate_position(game.board(), game.mainline_moves())
            
            evaluation = minimax.evaluate(board)
            mobility = len(list(board.legal_moves))
            outcome = convert_outcome(game.headers["Result"])

            evaluation_scores.append(evaluation)
            mobility_scores.append(mobility)
            outcomes.append(outcome)
        else:
            break
        i += 1
    data = []
    for i in range(0, sample_count):
        data.append([evaluation_scores[i], mobility_scores[i]])
        
    x_data = np.array(data)
    y_data = np.array(outcomes)

    return (x_data, y_data)

def initialise_centroids(X, k):
    np.random.seed(0)
    random_indices = np.random.permutation(X.shape[0])
    centroids = X[random_indices[:k]]
    return centroids

def assign_clusters(X, centroids):
    clusters = []
    for x in X:
        distances = np.linalg.norm(x - centroids, axis=1)
        cluster = np.argmin(distances)
        clusters.append(cluster)
    return np.array(clusters)

def update_centroids(X, clusters, k):
    new_centroids = []
    for i in range(k):
        cluster_points = X[clusters == i]
        new_centroid = cluster_points.mean(axis=0)
        new_centroids.append(new_centroid)
    return np.array(new_centroids)
    
def k_means(X, k, max_iters=100, tol=1e-4):
    centroids = initialise_centroids(X, k)
    for i in range(max_iters):
        clusters = assign_clusters(X, centroids)
        new_centroids = update_centroids(X, clusters, k)
        if np.all(np.abs(new_centroids - centroids) < tol):
            break
        centroids = new_centroids
    return centroids, clusters

def predict(new_data_point, centroids):
    distances = np.linalg.norm(new_data_point - centroids, axis=1)
    closest_centroid_index = np.argmin(distances)
    return closest_centroid_index

def main():
    data = initialise_data()
    X = data[0]
    y = data[1]
    k = 3
    final_centroids, final_clusters = k_means(X, k)

    # plt.scatter(X[:, 0], X[:, 1], c=final_clusters, s=50, cmap='viridis')
    # plt.scatter(final_centroids[:, 0], final_centroids[:, 1], s=200, c='red', alpha=0.75)
    # plt.title("K-Means Clustering Result")
    # plt.show()

    print("Cluster Centroids and Their Indices:")
    for i, centroid in enumerate(final_centroids):
        print(f"Cluster {i}: {centroid}")
    
    return final_centroids, final_clusters
if __name__ == "__main__":
    main()