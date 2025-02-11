import numpy as np

class Game:
    def __init__(self, difficulty=1):
        self.board = np.zeros((3, 3), dtype=int)
        self.player = 1  # 1 for player, -1 for AI
        self.difficulty = difficulty

    def make_move(self, row, col):
        if self.board[row, col] == 0:
            self.board[row, col] = self.player
            self.player *= -1  # Switch turns
            return True
        return False

    def to_dict(self):
        return {
            'board': self.board.tolist(),
            'player': self.player,
            'difficulty': self.difficulty
        }

    @classmethod
    def from_dict(cls, data):
        game = cls(data['difficulty'])
        game.board = np.array(data['board'])
        game.player = data['player']
        return game
