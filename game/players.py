import random
import math


class RandomPlayer:
    def play(self, game, symbol):
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

    def play(self, game, symbol):
        board = list(game.board)
        player = symbol
        opponent = 'O' if player == 'X' else 'X'

        win_move = self.find_winning_move(board, player)
        if win_move is not None:
            return win_move

        block_move = self.find_winning_move(board, opponent)
        if block_move is not None:
            return block_move

        if board[4] == ' ':
            return 4

        for (corner, opposite) in [(0, 8), (2, 6), (6, 2), (8, 0)]:
            if board[corner] == opponent and board[opposite] == ' ':
                return opposite

        corners = [0, 2, 6, 8]
        empty_corners = [c for c in corners if board[c] == ' ']
        if empty_corners:
            return random.choice(empty_corners)

        sides = [1, 3, 5, 7]
        empty_sides = [s for s in sides if board[s] == ' ']
        if empty_sides:
            return random.choice(empty_sides)

        return None

    def find_winning_move(self, board, player):
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values.count(player) == 2 and values.count(' ') == 1:
                return combo[values.index(' ')]
        return None


class LegendPlayer:
    WINNING_COMBINATIONS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]

    def play(self, game, symbol):
        board = list(game.board)
        move = self.find_best_move(board, symbol)
        return move

    def find_best_move(self, board, player):
        best_score = -math.inf
        best_move = None
        opponent = self.get_opponent(player)
        for i in self.get_move_order(board):
            if board[i] == ' ':
                board[i] = player
                score = self.minimax(board, 0, False, player, opponent, -math.inf, math.inf)
                board[i] = ' '
                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move

    def minimax(self, board, depth, is_maximizing, player, opponent, alpha, beta):
        winner = self.check_winner(board)
        if winner == player:
            return 100 - depth
        elif winner == opponent:
            return depth - 100
        elif ' ' not in board:
            return 0

        if is_maximizing:
            max_eval = -math.inf
            for i in self.get_move_order(board):
                if board[i] == ' ':
                    board[i] = player
                    eval = self.minimax(board, depth + 1, False, player, opponent, alpha, beta)
                    board[i] = ' '
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = math.inf
            for i in self.get_move_order(board):
                if board[i] == ' ':
                    board[i] = opponent
                    eval = self.minimax(board, depth + 1, True, player, opponent, alpha, beta)
                    board[i] = ' '
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval

    def get_move_order(self, board):
        # Prefer center, then corners, then sides
        return [4, 0, 2, 6, 8, 1, 3, 5, 7]

    def check_winner(self, board):
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values[0] != ' ' and values[0] == values[1] == values[2]:
                return values[0]
        return None

    def get_opponent(self, player):
        return 'O' if player == 'X' else 'X'


def get_player(player_name):
    # Handle case where player_name is a username (not an AI player)
    if player_name not in ['random', 'minimax', 'computer', 'game.players.RandomPlayer', 'game.players.GoodPlayer',
                           'game.players.LegendPlayer']:
        return RandomPlayer()  # Fallback to random AI

    # Map player types to their classes
    player_types = {
        'random': RandomPlayer,
        'computer': RandomPlayer,
        'minimax': LegendPlayer,
        'game.players.RandomPlayer': RandomPlayer,
        'game.players.GoodPlayer': GoodPlayer,
        'game.players.LegendPlayer': LegendPlayer
    }

    player_class = player_types.get(player_name.lower())
    if player_class is None:
        return RandomPlayer()  # Default fallback

    return player_class()
