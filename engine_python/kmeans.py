import minimax
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import random
import chess.pgn

CREATE_NEW_SAMPLE = False
SHOW_CLUSTERING_RESULT = False #Plot graph of clusters
SHOW_ELBOW = True #Plot distortion and inertia of clusters
ELBOW_COUNT = 10 #Max clusters for elbow 
PGN_PATH = "data/3000-4000.pgn"
SAMPLE_COUNT = 12000
CENTROID_COUNT = 12


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
    

def generate_sample(PGN_PATH, sample_count):
    pgn = open(PGN_PATH)
    filename = "%s.txt" % (str(sample_count) + "_samples")
    outcomeFile = "%s.txt" % (str(sample_count) + "_outcomes")
    i = 0
    while (i < sample_count):
        game = chess.pgn.read_game(pgn)
        move_count = 21 #was 35
        if game is not None:
            board = game.board()
            for move in game.mainline_moves():
                if board.is_game_over():
                    board.pop()
                    with open(filename, "a") as f:
                        f.write(board.board_fen())
                        f.write("\n")
                    break
                elif move_count % 7 == 0:
                    with open(filename, "a") as f:
                        f.write(board.board_fen())
                        f.write("\n")
                elif move_count < 0:
                    break
                board.push(move)
                move_count -= 1
            
            with open(outcomeFile, "a") as f:
                f.write(convert_outcome(game.headers["Result"]))
                f.write("\n")
        else:
            i -= 1
        i += 1

def generate_sample_randomly(PGN_PATH, sample_count):
    pgn = open(PGN_PATH)
    filename = "%s.txt" % (str(sample_count) + "_samples")
    outcomeFile = "%s.txt" % (str(sample_count) + "_outcomes")
    i = 0
    while (i < sample_count):
        game = chess.pgn.read_game(pgn)
        move_count = random.randint(1,30)
        if game is not None:
            board = game.board()
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
            with open(outcomeFile, "a") as f:
                f.write(convert_outcome(game.headers["Result"]))
                f.write("\n")
        else:
            i -= 1
        i += 1

#Improve to add more features
def extract_features(board: chess.Board):
    material = minimax.calculate_board_material(board)
    mobility = minimax.calculate_mobility(board)
    positioning = minimax.calculate_PST(board)
    centre_control = minimax.calculate_centre_control(board)
    king_safety = minimax.calculate_king_safety(board)
    return [material, positioning, mobility,  centre_control, king_safety]


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

def calculate_elbow(X, max_clusters):
    distortions = []
    inertias = []
    K = range(1, max_clusters)

    for k in K:
        centroids, clusters = k_means(X, k)
    
        distortions.append(sum(np.min(cdist(X, centroids, 'euclidean'), axis=1)**2) / X.shape[0])
        

        inertias.append(sum(np.min(cdist(X, centroids, 'euclidean'), axis=1)**2))

    plt.plot(K, distortions, 'bx-')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Distortion')
    plt.title('3000-4000 ELO, 12000 Samples Distortion')
    plt.grid()
    plt.show()

    plt.plot(K, inertias, 'bx-')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.title('3000-4000 ELO, 12000 Samples Inertia')
    plt.grid()
    plt.show()

def main():
    if CREATE_NEW_SAMPLE:
        generate_sample(PGN_PATH, SAMPLE_COUNT)
    X = initialise_data(SAMPLE_COUNT)
    final_centroids, final_clusters = k_means(X, CENTROID_COUNT)

    if SHOW_CLUSTERING_RESULT:
        plt.scatter(X[:, 0], X[:, 1], c=final_clusters, s=50, cmap='viridis')
        plt.scatter(final_centroids[:, 0], final_centroids[:, 1], s=200, c='red', alpha=0.75)
        plt.title("K-Means Clustering Result")
        plt.show()

    final_centroids = np.array(sorted(final_centroids, key=lambda final_centroids: final_centroids[0]))
    print("Cluster Centroids and Their Indices:")
    for i, centroid in enumerate(final_centroids):
        print(f"Cluster {i}: {centroid}")

    # Store clusters in csv
    filename = "KMeans_" + str(X.size) + "_" + str(CENTROID_COUNT) + "_clusters.csv"
    np.savetxt(filename, final_centroids, delimiter=",")

    if SHOW_ELBOW:
        calculate_elbow(X, ELBOW_COUNT)
    
    return final_centroids, final_clusters

if __name__ == "__main__":
    main()