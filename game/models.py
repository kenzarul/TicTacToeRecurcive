import random
from collections import Counter

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models


class Game(models.Model):
    room_code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    last_main_index = models.PositiveIntegerField(null=True, blank=True)
    last_sub_index = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    board = models.CharField(max_length=9, default=" " * 9)
    player_x = models.CharField(max_length=64, null=True, blank=True)
    player_o = models.CharField(max_length=64, null=True, blank=True)
    active_index = models.PositiveIntegerField(null=True, blank=True)
    winner = models.CharField(max_length=64, null=True, blank=True)

    def __unicode__(self):
        return '{0} vs {1}, state="{2}"'.format(self.player_x, self.player_o, self.board)

    def get_absolute_url(self):
        return reverse('game:detail', kwargs={'pk': self.pk})

    @property
    def next_player(self):
        boards = ''.join(self.sub_games.values_list('board', flat=True))
        count = Counter(boards)
        if count.get('X', 0) > count.get('O', 0):
            return 'O'
        return 'X'

    WINNING = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ]

    @property
    def is_game_over(self):
        board = list(self.board)
        for wins in self.WINNING:
            w = (board[wins[0]], board[wins[1]], board[wins[2]])
            if w == ('X', 'X', 'X'):
                self.winner = 'X'
                self.save()
                return 'X'
            if w == ('O', 'O', 'O'):
                self.winner = 'O'
                self.save()
                return 'O'
        if ' ' in board:
            return None
        return ' '  # Stalemate

    def play(self, main_index, sub_index):
        if self.active_index is not None and main_index != self.active_index:
            raise ValidationError("This is not the active board")
        if (main_index < 0 or main_index >= 9) or (sub_index < 0 or sub_index >= 9):
            raise IndexError("Invalid board index")
        if self.board[main_index] != ' ':
            return None

        sub_game = self.sub_games.filter(index=int(main_index)).first()
        if sub_game is None:
            raise ValueError("Invalid sub index")

        if sub_game.is_game_over is not None:
            available_subgrids = [i for i in range(9) if self.board[i] == ' ']
            self.set_active_index(random.choice(available_subgrids) if available_subgrids else None)
            return None

        winner = sub_game.play(sub_index)
        sub_game.save()

        self.last_main_index = main_index
        self.last_sub_index = sub_index
        self.save()

        board = list(self.board)
        if winner is not None:
            board[main_index] = winner
        elif ' ' not in sub_game.board:
            board[main_index] = ' '  # Draw
        self.board = ''.join(board)

        self.set_active_index(sub_index)
        return winner

    def set_active_index(self, index):
        self.active_index = None if self.board[index] != ' ' else index

    def play_auto(self):
        if not self.is_game_over:
            next = self.next_player
            player = self.player_x if next == 'X' else self.player_o
            if player == 'human':
                return

            from game.players import get_player  # ✅ Lazy import here

            if self.active_index is None:
                open_indexes = [i for i, v in enumerate(self.board) if v == ' ']
                main_index = random.choice(open_indexes)
            else:
                main_index = self.active_index

            player_obj = get_player(player)
            sub_game = self.sub_games.filter(index=main_index).first()
            sub_index = player_obj.play(sub_game)
            self.play(main_index, sub_index)


class SubGame(models.Model):
    last_move_index = models.PositiveIntegerField(null=True, blank=True)
    last_computer_move = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sub_games')
    index = models.PositiveIntegerField()
    board = models.CharField(max_length=9, default=" " * 9)
    player_x = models.CharField(max_length=64)
    player_o = models.CharField(max_length=64)
    winner = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"Game {self.game.pk} - Index {self.index}"

    def __unicode__(self):
        return '{0} vs {1}, state="{2}"'.format(self.player_x, self.player_o, self.board)

    def get_absolute_url(self):
        return reverse('game:detail', kwargs={'pk': self.pk})

    @property
    def next_player(self):
        boards = ''.join(self.game.sub_games.values_list('board', flat=True))
        count = Counter(boards)
        return 'O' if count.get('X', 0) > count.get('O', 0) else 'X'

    WINNING = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ]

    @property
    def is_game_over(self):
        board = list(self.board)
        for wins in self.WINNING:
            w = (board[wins[0]], board[wins[1]], board[wins[2]])
            if w == ('X', 'X', 'X'):
                self.winner = 'X'
                self.save()
                return 'X'
            if w == ('O', 'O', 'O'):
                self.winner = 'O'
                self.save()
                return 'O'
        if ' ' in board:
            return None
        return ' '  # Draw

    def play(self, index):
        if index < 0 or index >= 9:
            raise IndexError("Invalid board index")
        if self.board[index] != ' ':
            raise ValueError("Square already played")

        board = list(self.board)
        board[index] = self.next_player
        self.board = ''.join(board)

        self.last_move_index = index
        self.save()
        return self.is_game_over

    def play_auto(self):
        if not self.is_game_over:
            next = self.next_player
            player = self.player_x if next == 'X' else self.player_o
            if player == 'human':
                return

            from game.players import get_player  # ✅ Lazy import here

            player_obj = get_player(player)
            sub_index = player_obj.play(self)

            self.play(sub_index)
            self.last_move_index = sub_index
            self.save()
