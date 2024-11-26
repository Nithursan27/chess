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
    string fenBoard = board.getFen();
    string pieces = fenBoard.substr(0, fenBoard.find(' '));
    for (auto &piece : pieces)
    {
        if (pieceValues.contains(piece))
        {
            advantage += pieceValues[piece];
        }
    }
    cout << pieces << endl;
    cout << advantage << endl;
    return advantage;
}

int main()
{
    Board board = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    calculateMaterial(board);
    return 0;
}