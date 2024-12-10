#include "chess.hpp"
#include <iostream>
#include <vector>
#include <map>

using namespace chess;
using namespace std;

map<char, int> pieceValues{{'p', -1}, {'n', -3}, {'b', -3}, {'r', -5}, {'q', -9}, {'P', 1}, {'N', 3}, {'B', 3}, {'R', 5}, {'Q', 9}};

// Calculates the raw material advantage
int calculateMaterial(Board &board)
{
    int advantage = 0;
    string fenBoard = board.getFen(false);
    string pieces = fenBoard.substr(0, fenBoard.find(' '));
    for (auto &piece : pieces)
    {
        if (pieceValues.contains(piece))
        {
            advantage += pieceValues[piece];
        }
    }
    // cout << pieces << endl;
    // cout << advantage << endl;
    return advantage;
}

int evaluate(Board &board)
{
    return calculateMaterial(board);
}

int minimax(Board board, int depth, int alpha, int beta, bool isMax)
{
    if (depth == 0) // add game over condition as OR check
    {
        return evaluate(board);
    }

    Movelist moves;
    movegen::legalmoves(moves, board);

    if (isMax)
    {
        int maxEval = INT_MIN;
        for (auto &move : moves)
        {
            board.makeMove(move);
            int eval = minimax(board, depth - 1, alpha, beta, false);
            board.unmakeMove(move);
            maxEval = max(maxEval, eval);
            alpha = max(alpha, maxEval);
            if (beta <= alpha)
            {
                break;
            }
        }
        return maxEval;
    }

    else
    {
        int minEval = INT_MAX;
        for (auto &move : moves)
        {
            board.makeMove(move);
            int eval = minimax(board, depth - 1, alpha, beta, true);
            board.unmakeMove(move);
            minEval = min(minEval, eval);
            beta = min(beta, minEval);
            if (beta <= alpha)
            {
                break;
            }
        }
        return minEval;
    }
}

int main()
{
    Board board = Board("rnbqkbnr/pppppppp/8/1r1n4/2P5/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    // Board board = Board("4k3/8/8/1p1n4/2P5/8/8/4KP2 w ---- - 0 1");
    cout << "best move leads to: " << minimax(board, 1, INT_MIN, INT_MAX, true) << endl;
    return 1;
}