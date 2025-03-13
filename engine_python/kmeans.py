import minimax
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

import chess.pgn

CREATE_NEW_SAMPLE = False
PGN_PATH = "data/2500-4000.pgn"
SAMPLE_COUNT = 1000
CLUSTER_SIZE = 3

def generate_sample(PGN_PATH, sample_count):
    pgn = open(PGN_PATH)
    filename = "%s.txt" % (str(sample_count) + "_samples")
    i = 0
    while (i < sample_count):
        game = chess.pgn.read_game(pgn)
        board = game.board()
        move_count = random.randint(1,30)
        if game is not None:
            for move in game.mainline_moves():
                if board.is_game_over():
                    board.pop()
                    break
                elif move_count <= 0:
                    break
                board.push(move)
                move_count -= 1
            
            with open(filename, "a") as f:
                f.write(board.board_fen())
                f.write("\n")
        else:
            i -= 1
        i += 1

def extract_features(board: chess.Board):
    eval = minimax.evaluate(board)
    mobility = len(list(board.legal_moves))
    positioning = minimax.calculate_PST(board)
    return [eval, mobility, positioning]

#Improve to add more features
def extract_prediction_data(board: chess.Board):
    return np.array(extract_features(board))

def initialise_data(sample_count):
    data = []
    filename = "%s.txt" % (str(sample_count) + "_samples")
    with open(filename, "r") as file:
        for line in file:
            if not line.isspace():
                board = chess.Board(line.strip())

                data.append(extract_features(board))

    return np.array(data)

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
    if CREATE_NEW_SAMPLE:
        generate_sample(PGN_PATH, SAMPLE_COUNT)
    X = initialise_data(SAMPLE_COUNT)
    final_centroids, final_clusters = k_means(X, CLUSTER_SIZE)

    plt.scatter(X[:, 0], X[:, 1], c=final_clusters, s=50, cmap='viridis')
    plt.scatter(final_centroids[:, 0], final_centroids[:, 1], s=200, c='red', alpha=0.75)
    plt.title("K-Means Clustering Result")
    plt.show()

    print("Cluster Centroids and Their Indices:")
    for i, centroid in enumerate(final_centroids):
        print(f"Cluster {i}: {centroid}")

    filename = "KMeans_" + str(X.size) + "_" + str(CLUSTER_SIZE) + "_clusters.txt"
    with open(filename, "w") as f:
        for centroid in final_centroids:
            f.write(f"{centroid}")
            f.write("\n")
    
    return final_centroids, final_clusters

if __name__ == "__main__":
    main()