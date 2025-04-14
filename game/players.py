import math
import random
from functools import lru_cache


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
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]  # diagonals
    ]

    # Board importance matrix (center is most valuable)
    BOARD_IMPORTANCE = [
        3, 2, 3,
        2, 4, 2,
        3, 2, 3
    ]

    def __init__(self, depth=3, use_alpha_beta=True):
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.transposition_table = {}

    def play(self, game):
        if hasattr(game, 'sub_games'):
            return self.play_ultimate(game)
        return self.play_regular(game)

    def play_ultimate(self, game):
        player = game.next_player
        opponent = 'O' if player == 'X' else 'X'

        # First check if we can win the global game immediately
        global_win_move = self.check_global_win_opportunity(game, player)
        if global_win_move is not None:
            return global_win_move[1]

        # Check if we need to block opponent from winning globally
        global_block_move = self.check_global_win_opportunity(game, opponent)
        if global_block_move is not None:
            return global_block_move[1]

        # Check for potential diagonal threats
        diagonal_block_move = self.check_diagonal_threat(game, opponent)
        if diagonal_block_move is not None:
            return diagonal_block_move[1]

        # Get active subgame index
        active_index = game.active_index

        # If no active index (free choice), choose most strategic board
        if active_index is None:
            active_index = self.choose_most_strategic_board(game)

        # Get the subgame
        sub_game = game.sub_games.filter(index=active_index).first()

        # Find best move considering both local and global strategy
        best_move = self.find_best_ultimate_move(game, sub_game, player, opponent)

        return best_move if best_move is not None else random.choice(
            [i for i, s in enumerate(sub_game.board) if s == ' '])

    def check_diagonal_threat(self, game, opponent):
        """Check for potential diagonal threats where opponent has 2 in a diagonal"""
        main_board = game.board
        diagonals = [[0, 4, 8], [2, 4, 6]]  # The two possible diagonals

        for diagonal in diagonals:
            values = [main_board[i] for i in diagonal]

            # Check if opponent has 2 in this diagonal with one empty
            if values.count(opponent) == 2 and values.count(' ') == 1:
                empty_pos = diagonal[values.index(' ')]
                sub_game = game.sub_games.filter(index=empty_pos).first()

                if sub_game and sub_game.is_game_over is None:
                    # Try to take center first
                    if sub_game.board[4] == ' ':
                        return (empty_pos, 4)

                    # Then try to take a corner
                    corners = [0, 2, 6, 8]
                    empty_corners = [c for c in corners if sub_game.board[c] == ' ']
                    if empty_corners:
                        return (empty_pos, random.choice(empty_corners))

                    # Then any available move
                    available = [i for i in range(9) if sub_game.board[i] == ' ']
                    if available:
                        return (empty_pos, random.choice(available))

        return None

    def check_global_win_opportunity(self, game, player):
        """Check if we can win the global game immediately by winning a subgame"""
        main_board = game.board
        opponent = 'O' if player == 'X' else 'X'

        for main_index in [i for i, v in enumerate(main_board) if v == ' ']:
            sub_game = game.sub_games.filter(index=main_index).first()
            if sub_game.is_game_over is not None:
                continue

            # Check if winning this subgame would win the global game
            temp_main = list(main_board)
            temp_main[main_index] = player
            if self.evaluate_winner(''.join(temp_main)) == player:
                # Now find a winning move in this subgame
                winning_move = self.find_winning_move(sub_game.board, player)
                if winning_move is not None:
                    return (main_index, winning_move)

        return None

    def find_best_ultimate_move(self, game, sub_game, player, opponent):
        """Find the best move considering both local and global strategy"""
        board = sub_game.board
        main_index = sub_game.index

        # First check for immediate wins/blocks in the subgame
        immediate_move = self.check_immediate_moves(board, player, opponent)
        if immediate_move is not None:
            return immediate_move

        # Then consider the global strategy
        moves = self.get_ordered_moves(board, player, opponent)

        best_move = None
        best_score = -math.inf

        for move in moves:
            score = 0

            # Simulate the move
            new_sub_board = board[:move] + player + board[move + 1:]

            # 1. Check if this wins the subgame
            subgame_result = self.evaluate_winner(new_sub_board)

            if subgame_result == player:
                # Winning a subgame is good - but consider global implications
                temp_main = list(game.board)
                temp_main[main_index] = player

                # Check if this wins the global game
                if self.evaluate_winner(''.join(temp_main)) == player:
                    score += 1000
                # Check if this creates a global fork
                elif self.count_global_threats(game, main_index, player) >= 2:
                    score += 500
                else:
                    # Base value for winning a subgame
                    score += 100 + self.BOARD_IMPORTANCE[main_index] * 10

            # 2. Check if move prevents opponent from winning global game
            opponent_temp_main = list(game.board)
            opponent_temp_main[main_index] = opponent
            if self.evaluate_winner(''.join(opponent_temp_main)) == opponent:
                if subgame_result is None:  # If we don't win it ourselves
                    score += 800

            # 3. Extra bonus for blocking diagonal threats
            if self.is_diagonal_block(main_index, move, game, opponent):
                score += 300

            # 4. Positional advantages
            if move == 4:  # Center
                score += 5
            elif move in [0, 2, 6, 8]:  # Corners
                score += 3

            # 5. The board we're sending opponent to
            next_board = move
            if game.board[next_board] == ' ':
                score += (9 - self.BOARD_IMPORTANCE[next_board]) * 2

            # 6. Check for local forks
            if self.is_fork_opportunity(board, move, player):
                score += 10

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def is_diagonal_block(self, main_index, move, game, opponent):
        """Check if this move helps block a diagonal threat"""
        diagonals = [[0, 4, 8], [2, 4, 6]]
        for diagonal in diagonals:
            if main_index in diagonal:
                other_positions = [p for p in diagonal if p != main_index]
                if (game.board[other_positions[0]] == opponent and
                        game.board[other_positions[1]] == opponent):
                    return True
        return False

    def count_global_threats(self, game, main_index, player):
        """Count how many winning lines this subgame win would create"""
        temp_main = list(game.board)
        temp_main[main_index] = player
        count = 0

        for combo in self.WINNING_COMBINATIONS:
            values = [temp_main[i] for i in combo]
            if values.count(player) == 2 and values.count(' ') == 1:
                count += 1
        return count

    def choose_most_strategic_board(self, game):
        """Choose the most strategically valuable available board"""
        available_boards = [i for i in range(9) if game.board[i] == ' ']

        # Prefer center board
        if 4 in available_boards:
            return 4

        # Then prefer corners
        corners = [0, 2, 6, 8]
        available_corners = [c for c in corners if c in available_boards]
        if available_corners:
            return random.choice(available_corners)

        # Then any available board
        return random.choice(available_boards)

    def check_immediate_moves(self, board, player, opponent):
        """Check for immediate wins or blocks"""
        # Check for immediate win
        win_move = self.find_winning_move(board, player)
        if win_move is not None:
            return win_move

        # Check for immediate block
        block_move = self.find_winning_move(board, opponent)
        if block_move is not None:
            return block_move

        # Check for fork opportunities
        fork_move = self.find_fork(board, player, opponent)
        if fork_move is not None:
            return fork_move

        return None

    def find_winning_move(self, board, player):
        """Find an immediate winning move"""
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values.count(player) == 2 and values.count(' ') == 1:
                return combo[values.index(' ')]
        return None

    def find_fork(self, board, player, opponent):
        """Find moves that create two ways to win (forks)"""
        fork_moves = []
        for move in [i for i, v in enumerate(board) if v == ' ']:
            new_board = board[:move] + player + board[move + 1:]
            winning_lines = 0
            for combo in self.WINNING_COMBINATIONS:
                values = [new_board[i] for i in combo]
                if values.count(player) == 2 and values.count(' ') == 1:
                    winning_lines += 1
                    if winning_lines >= 2:
                        fork_moves.append(move)
                        break

        if fork_moves:
            if 4 in fork_moves:  # Prefer center
                return 4
            corners = [0, 2, 6, 8]
            for corner in corners:
                if corner in fork_moves:
                    return corner
            return fork_moves[0]

        # Block opponent forks
        opponent_forks = []
        for move in [i for i, v in enumerate(board) if v == ' ']:
            new_board = board[:move] + opponent + board[move + 1:]
            winning_lines = 0
            for combo in self.WINNING_COMBINATIONS:
                values = [new_board[i] for i in combo]
                if values.count(opponent) == 2 and values.count(' ') == 1:
                    winning_lines += 1
                    if winning_lines >= 2:
                        opponent_forks.append(move)
                        break

        if opponent_forks:
            if 4 in opponent_forks:
                return 4
            corners = [0, 2, 6, 8]
            for corner in corners:
                if corner in opponent_forks:
                    return corner
            return opponent_forks[0]

        return None

    def is_fork_opportunity(self, board, move, player):
        """Check if a move creates a fork"""
        temp_board = board[:move] + player + board[move + 1:]
        winning_lines = 0
        for combo in self.WINNING_COMBINATIONS:
            values = [temp_board[i] for i in combo]
            if values.count(player) == 2 and values.count(' ') == 1:
                winning_lines += 1
                if winning_lines >= 2:
                    return True
        return False

    def get_ordered_moves(self, board, player, opponent):
        """Returns moves ordered by heuristic importance"""
        empty_spots = [i for i, spot in enumerate(board) if spot == ' ']
        moves = []

        for move in empty_spots:
            score = 0
            if move == 4:  # Center
                score += 4
            elif move in [0, 2, 6, 8]:  # Corner
                score += 3
            elif move in [1, 3, 5, 7]:  # Edge
                score += 1

            # Check for potential forks
            temp_board = board[:move] + player + board[move + 1:]
            if self.count_potential_wins(temp_board, player) >= 2:
                score += 2

            moves.append((score, move))

        moves.sort(reverse=True, key=lambda x: x[0])
        return [m[1] for m in moves]

    def count_potential_wins(self, board, player):
        """Count how many winning lines a player could complete"""
        count = 0
        for combo in self.WINNING_COMBINATIONS:
            values = [board[i] for i in combo]
            if values.count(player) >= 1 and values.count(' ') >= 1:
                count += 1
        return count

    def evaluate_winner(self, board):
        """Check if a board has been won"""
        for combo in self.WINNING_COMBINATIONS:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
                return board[combo[0]]
        return None

    def play_regular(self, game):
        """Perfect play for regular tic-tac-toe"""
        board = game.board
        player = game.next_player
        opponent = 'O' if player == 'X' else 'X'

        # Check for immediate win
        win_move = self.find_winning_move(board, player)
        if win_move is not None:
            return win_move

        # Check for immediate block
        block_move = self.find_winning_move(board, opponent)
        if block_move is not None:
            return block_move

        # Take center if available
        if board[4] == ' ':
            return 4

        # Take opposite corner if opponent is in corner
        for (corner, opposite) in [(0, 8), (2, 6), (6, 2), (8, 0)]:
            if board[corner] == opponent and board[opposite] == ' ':
                return opposite

        # Take any empty corner
        corners = [0, 2, 6, 8]
        empty_corners = [c for c in corners if board[c] == ' ']
        if empty_corners:
            return random.choice(empty_corners)

        # Take any empty side
        sides = [1, 3, 5, 7]
        empty_sides = [s for s in sides if board[s] == ' ']
        if empty_sides:
            return random.choice(empty_sides)

        return None


def get_player(player_name):
    if player_name == 'game.players.GoodPlayer':
        return GoodPlayer()
    elif player_name == 'game.players.LegendPlayer':
        return LegendPlayer()
    elif player_name == 'game.players.RandomPlayer':
        return RandomPlayer()
    raise ValueError(f"Unknown player: {player_name}")

