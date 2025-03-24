import math
import random
from django.utils.module_loading import import_string

class RandomPlayer:
    def play(self, game):
        open_indexes = [i for i, v in enumerate(game.board) if v == ' ']
        if not open_indexes:
            return
        return random.choice(open_indexes)

class GoodPlayer:
    WINNING_COMBINATIONS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    POSITION_SCORES = [
        3, 2, 3,
        2, 4, 2,
        3, 2, 3
    ]

    def play(self, game):
        board = list(game.board)
        player = game.next_player
        opponent = 'O' if player == 'X' else 'X'

        for strategy in [self.find_winning_move, self.find_winning_move, self.find_fork, self.find_fork]:
            move = strategy(board, player if strategy != self.find_winning_move else opponent)
            if move is not None:
                return move

        if board[4] == ' ':
            return 4

        for (corner, opposite) in [(0, 8), (2, 6), (6, 2), (8, 0)]:
            if board[corner] == opponent and board[opposite] == ' ':
                return opposite

        best_moves = sorted([(self.POSITION_SCORES[i], i) for i in range(9) if board[i] == ' '], reverse=True)
        return best_moves[0][1] if best_moves else None

    def find_winning_move(self, board, player):
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values.count(player) == 2 and values.count(' ') == 1:
                return combo[values.index(' ')]
        return None

    def find_fork(self, board, player):
        for move in [i for i, v in enumerate(board) if v == ' ']:
            board_copy = board[:]
            board_copy[move] = player
            if sum(1 for combo in self.WINNING_COMBINATIONS if [board_copy[i] for i in combo].count(player) == 2 and [board_copy[i] for i in combo].count(' ') == 1) >= 2:
                return move
        return None

#cann't be used yet the depth is not yet configured
class LegendPlayer:
    WINNING_COMBINATIONS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    POSITION_SCORES = [
        3, 2, 3,
        2, 4, 2,
        3, 2, 3
    ]

    def play(self, game):
        board = list(game.board)
        player = game.next_player
        best_score = -math.inf
        best_move = None

        for i in range(9):
            if board[i] == ' ':
                board[i] = player
                score = self.minimax(board, 0, False, player, 'O' if player == 'X' else 'X', -math.inf, math.inf)
                board[i] = ' '
                if score > best_score:
                    best_score = score
                    best_move = i

        return best_move

    def minimax(self, board, depth, is_maximizing, ai_player, human_player, alpha, beta):
        winner = self.evaluate_winner(board)
        if winner == ai_player:
            return 10 - depth
        elif winner == human_player:
            return depth - 10
        elif ' ' not in board:
            return 0

        best_score = -math.inf if is_maximizing else math.inf
        for i in self.get_sorted_moves(board, ai_player if is_maximizing else human_player):
            board[i] = ai_player if is_maximizing else human_player
            score = self.minimax(board, depth + 1, not is_maximizing, ai_player, human_player, alpha, beta)
            board[i] = ' '
            best_score = max(best_score, score) if is_maximizing else min(best_score, score)
            if is_maximizing:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)
            if beta <= alpha:
                break
        return best_score

    def evaluate_winner(self, board):
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values == ['X', 'X', 'X']:
                return 'X'
            elif values == ['O', 'O', 'O']:
                return 'O'
        return None

    def get_sorted_moves(self, board, player):
        best_moves = sorted([(self.POSITION_SCORES[i], i) for i in range(9) if board[i] == ' '], reverse=True)
        return [i for _, i in best_moves]

def get_player(player_name):
    if player_name == 'game.players.GoodPlayer':
        return GoodPlayer()
    elif player_name == 'game.players.LegendPlayer':
        return LegendPlayer()
    elif player_name == 'game.players.RandomPlayer':
        return RandomPlayer()
    raise ValueError(f"Unknown player: {player_name}")

