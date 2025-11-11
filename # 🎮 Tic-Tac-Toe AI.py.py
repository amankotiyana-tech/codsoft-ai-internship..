# 🎮 Tic-Tac-Toe AI (Minimax with Alpha-Beta Pruning)
# Author: Aman Kotiyana
# Course: BCA 3rd Year
# Internship Task: CodeSoft - AI Project

import math
import random

def print_board(board):
    print()
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print()

def winner(board):
    combos = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in combos:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None

def available_moves(board):
    return [i for i,x in enumerate(board) if x==" "]

def minimax(board, depth, alpha, beta, is_max, ai, human):
    win = winner(board)
    if win == ai: return 10, None
    if win == human: return -10, None
    if " " not in board: return 0, None

    if is_max:
        best = -math.inf; move = None
        for m in available_moves(board):
            board[m] = ai
            score, _ = minimax(board, depth+1, alpha, beta, False, ai, human)
            board[m] = " "
            if score > best:
                best = score; move = m
            alpha = max(alpha, score)
            if beta <= alpha: break
        return best, move
    else:
        best = math.inf; move = None
        for m in available_moves(board):
            board[m] = human
            score, _ = minimax(board, depth+1, alpha, beta, True, ai, human)
            board[m] = " "
            if score < best:
                best = score; move = m
            beta = min(beta, score)
            if beta <= alpha: break
        return best, move

def ai_move(board, ai, human):
    if board.count(" ") == 9: return random.choice([0,2,4,6,8])
    _, move = minimax(board, 0, -math.inf, math.inf, True, ai, human)
    return move

def human_move(board):
    while True:
        move = input("Your move (1-9): ")
        if move.isdigit() and int(move)-1 in available_moves(board):
            return int(move)-1
        print("Invalid move, try again!")

def play():
    print("=== TIC TAC TOE ===")
    print(" 1 | 2 | 3 \n---+---+---\n 4 | 5 | 6 \n---+---+---\n 7 | 8 | 9 ")
    human = input("Choose your symbol (X/O): ").upper()
    ai = "O" if human=="X" else "X"
    board = [" "] * 9
    turn = "human"
    print_board(board)
    while True:
        if turn == "human":
            m = human_move(board)
            board[m] = human
            turn = "ai"
        else:
            print("AI thinking...")
            m = ai_move(board, ai, human)
            board[m] = ai
            turn = "human"
        print_board(board)
        win = winner(board)
        if win or " " not in board:
            if win == human: print("🎉 You win!")
            elif win == ai: print("💀 AI wins!")
            else: print("🤝 Draw!")
            break

if __name__ == "__main__":
    play()