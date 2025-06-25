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
        # Move ordering: center, corners, sides
        move_order = [4, 0, 2, 6, 8, 1, 3, 5, 7]
        for i in move_order:
            if board[i] == ' ':
                board[i] = player
                score = self.minimax(board, 0, False, player, opponent)
                board[i] = ' '
                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move

    def minimax(self, board, depth, is_maximizing, player, opponent):
        winner = self.check_winner(board)
        if winner == player:
            return 100 - depth
        elif winner == opponent:
            return depth - 100
        elif ' ' not in board:
            return 0

        if is_maximizing:
            best_score = -math.inf
            for i in range(9):
                if board[i] == ' ':
                    board[i] = player
                    score = self.minimax(board, depth + 1, False, player, opponent)
                    board[i] = ' '
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = math.inf
            for i in range(9):
                if board[i] == ' ':
                    board[i] = opponent
                    score = self.minimax(board, depth + 1, True, player, opponent)
                    board[i] = ' '
                    best_score = min(score, best_score)
            return best_score

    def check_winner(self, board):
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values[0] != ' ' and values[0] == values[1] == values[2]:
                return values[0]
        return None

    def get_opponent(self, player):
        return 'O' if player == 'X' else 'X'


def get_player(player_name):
    if player_name == 'game.players.RandomPlayer':
        return RandomPlayer()
    elif player_name == 'game.players.GoodPlayer':
        return GoodPlayer()
    elif player_name == 'game.players.LegendPlayer':
        return LegendPlayer()
    raise ValueError(f"Unknown player: {player_name}")
