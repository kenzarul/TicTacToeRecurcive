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

        # 1. Check for immediate win
        win_move = self.find_winning_move(board, player)
        if win_move is not None:
            return win_move

        # 2. Block opponent's immediate win
        block_move = self.find_winning_move(board, opponent)
        if block_move is not None:
            return block_move

        # 3. Try to create a fork
        fork_move = self.find_fork(board, player)
        if fork_move is not None:
            return fork_move

        # 4. Take center if available
        if board[4] == ' ':
            return 4

        # 5. Take opposite corner if opponent is in corner
        for (corner, opposite) in [(0, 8), (2, 6), (6, 2), (8, 0)]:
            if board[corner] == opponent and board[opposite] == ' ':
                return opposite

        # 6. Take any empty corner
        corners = [0, 2, 6, 8]
        empty_corners = [c for c in corners if board[c] == ' ']
        if empty_corners:
            return random.choice(empty_corners)

        # 7. Take any empty side
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

    def find_fork(self, board, player):
        # Find moves that create two ways to win
        for move in [i for i, v in enumerate(board) if v == ' ']:
            board_copy = board[:]
            board_copy[move] = player
            winning_moves = 0
            for combo in self.WINNING_COMBINATIONS:
                values = [board_copy[i] for i in combo]
                if values.count(player) == 2 and values.count(' ') == 1:
                    winning_moves += 1
                    if winning_moves >= 2:
                        return move
        return None


class LegendPlayer:
    WINNING_COMBINATIONS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]

    def play(self, game):
        board = list(game.board)
        player = game.next_player
        opponent = 'O' if player == 'X' else 'X'
        best_score = -math.inf
        best_move = None

        # First check for immediate wins/blocks
        immediate_move = self.check_immediate_moves(board, player, opponent)
        if immediate_move is not None:
            return immediate_move

        # Then use minimax for deeper analysis
        for i in range(9):
            if board[i] == ' ':
                board[i] = player
                score = self.minimax(board, 0, False, player, opponent)
                board[i] = ' '
                if score > best_score:
                    best_score = score
                    best_move = i

        return best_move if best_move is not None else random.choice([i for i, v in enumerate(board) if v == ' '])

    def minimax(self, board, depth, is_maximizing, ai_player, human_player):
        winner = self.evaluate_winner(board)
        if winner == ai_player:
            return 10 - depth
        elif winner == human_player:
            return depth - 10
        elif ' ' not in board:
            return 0

        if is_maximizing:
            best_score = -math.inf
            for i in range(9):
                if board[i] == ' ':
                    board[i] = ai_player
                    score = self.minimax(board, depth + 1, False, ai_player, human_player)
                    board[i] = ' '
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = math.inf
            for i in range(9):
                if board[i] == ' ':
                    board[i] = human_player
                    score = self.minimax(board, depth + 1, True, ai_player, human_player)
                    board[i] = ' '
                    best_score = min(score, best_score)
            return best_score

    def check_immediate_moves(self, board, player, opponent):
        # Check for immediate win
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values.count(player) == 2 and values.count(' ') == 1:
                return combo[values.index(' ')]

        # Check for immediate block
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values.count(opponent) == 2 and values.count(' ') == 1:
                return combo[values.index(' ')]
        return None

    def evaluate_winner(self, board):
        for combo in self.WINNING_COMBINATIONS:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
                return board[combo[0]]
        return None

def get_player(player_name):
    if player_name == 'game.players.GoodPlayer':
        return GoodPlayer()
    elif player_name == 'game.players.LegendPlayer':
        return LegendPlayer()
    elif player_name == 'game.players.RandomPlayer':
        return RandomPlayer()
    raise ValueError(f"Unknown player: {player_name}")

