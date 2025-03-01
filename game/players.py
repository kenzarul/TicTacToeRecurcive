"""
Players are defined their "play" method, which takes a game model
(or an object that proxies a game model, in such a way they aren't
allowed to perform any illegal actions).

They are expected to return an index that is their play.
"""
import random
from django.utils.module_loading import import_string


class RandomPlayer(object):
    """
    The random player plays in a random square. It's not very smart.
    """

    def play(self, game):
        # Find a spot on the board that's open.
        open_indexes = [i for i, v in enumerate(game.board) if v == ' ']
        # We probably shouldn't have been called, we can't play!
        if not open_indexes:
            return
        return random.choice(open_indexes)


def get_player(player_type):
    """
    This uses importlib to load the class.
    Since we don't have that many player types, you could hardcode types
    as well.
    """
    cls = import_string(player_type)
    return cls()




import random

class GoodPlayer:
    WINNING_COMBINATIONS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]

    def play(self, game):
        board = list(game.board)
        player = game.next_player
        opponent = 'O' if player == 'X' else 'X'

        # 1. Win if possible
        move = self.find_winning_move(board, player)
        if move is not None:
            return move

        # 2. Block the opponent from winning
        move = self.find_winning_move(board, opponent)
        if move is not None:
            return move

        # 3. Create a fork opportunity
        move = self.find_fork(board, player)
        if move is not None:
            return move

        # 4. Block the opponent's fork
        move = self.find_fork(board, opponent)
        if move is not None:
            return move

        # 5. Play the center
        if board[4] == ' ':
            return 4

        # 6. Play an opposite corner
        opposite_corners = [(0, 8), (2, 6), (6, 2), (8, 0)]
        for (corner, opposite) in opposite_corners:
            if board[corner] == opponent and board[opposite] == ' ':
                return opposite

        # 7. Play an empty corner
        for i in [0, 2, 6, 8]:
            if board[i] == ' ':
                return i

        # 8. Play an empty side
        for i in [1, 3, 5, 7]:
            if board[i] == ' ':
                return i

        # Fallback: Choose any available move
        available_moves = [i for i, v in enumerate(board) if v == ' ']
        return random.choice(available_moves)

    def find_winning_move(self, board, player):
        """Return the index of a winning move if available."""
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values.count(player) == 2 and values.count(' ') == 1:
                return combo[values.index(' ')]
        return None

    def find_fork(self, board, player):
        """Return the index of a fork-creating move if available."""
        available_moves = [i for i, v in enumerate(board) if v == ' ']
        for move in available_moves:
            board_copy = board[:]
            board_copy[move] = player
            winning_moves = sum(
                1 for combo in self.WINNING_COMBINATIONS
                if [board_copy[i] for i in combo].count(player) == 2 and
                   [board_copy[i] for i in combo].count(' ') == 1
            )
            if winning_moves >= 2:
                return move
        return None




import math

class LegendPlayer:
    WINNING_COMBINATIONS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
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
            return 0  # Draw

        if is_maximizing:
            best_score = -math.inf
            for i in range(9):
                if board[i] == ' ':
                    board[i] = ai_player
                    score = self.minimax(board, depth + 1, False, ai_player, human_player, alpha, beta)
                    board[i] = ' '
                    best_score = max(score, best_score)
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        break  # Pruning
            return best_score
        else:
            best_score = math.inf
            for i in range(9):
                if board[i] == ' ':
                    board[i] = human_player
                    score = self.minimax(board, depth + 1, True, ai_player, human_player, alpha, beta)
                    board[i] = ' '
                    best_score = min(score, best_score)
                    beta = min(beta, score)
                    if beta <= alpha:
                        break  # Pruning
            return best_score

    def evaluate_winner(self, board):
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values == ['X', 'X', 'X']:
                return 'X'
            elif values == ['O', 'O', 'O']:
                return 'O'
        return None




def get_player(player_name):
    if player_name == 'game.players.GoodPlayer':
        return GoodPlayer()
    elif player_name == 'game.players.LegendPlayer':
        return LegendPlayer()
    # Existing player registrations
    elif player_name == 'game.players.RandomPlayer':
        return RandomPlayer()
    # Add more players here as needed
    raise ValueError(f"Unknown player: {player_name}")