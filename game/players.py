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


def get_player(player_name):
    if player_name == 'game.players.RandomPlayer':
        return RandomPlayer()
    elif player_name == 'game.players.GoodPlayer':
        return GoodPlayer()
    elif player_name == 'game.players.LegendPlayer':
        return LegendPlayer()
    raise ValueError(f"Unknown player: {player_name}")
