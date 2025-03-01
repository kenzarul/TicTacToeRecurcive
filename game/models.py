import random
from collections import Counter

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models


class Game(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    board = models.CharField(max_length=9, default=" " * 9)

    player_x = models.CharField(max_length=64)
    player_o = models.CharField(max_length=64)
    active_index = models.PositiveIntegerField(null=True, blank=True)
    winner = models.CharField(max_length=64, null=True, blank=True)


    def __unicode__(self):
        return '{0} vs {1}, state="{2}"'.format(self.player_x, self.player_o, self.board)

    def get_absolute_url(self):
        return reverse('game:detail', kwargs={'pk': self.pk})

    @property
    def next_player(self):

        # Counter is a useful class that counts objects.
        boards = ''.join(self.sub_games.values_list('board', flat=True))
        count = Counter(boards)
        if count.get('X', 0) > count.get('O', 0):
            return 'O'
        return 'X'

    WINNING = [
        [0, 1, 2],  # Across top
        [3, 4, 5],  # Across middle
        [6, 7, 8],  # Across bottom
        [0, 3, 6],  # Down left
        [1, 4, 7],  # Down middle
        [2, 5, 8],  # Down right
        [0, 4, 8],  # Diagonal ltr
        [2, 4, 6],  # Diagonal rtl
    ]

    @property
    def is_game_over(self):

        board = list(self.board)
        for wins in self.WINNING:
            # Create a tuple
            w = (board[wins[0]], board[wins[1]], board[wins[2]])
            if w == ('X', 'X', 'X'):
                self.winner = 'X'
                self.save()
                return 'X'
            if w == ('O', 'O', 'O'):
                self.winner = 'O'
                self.save()
                return 'O'
        # Check for stalemate
        if ' ' in board:
            return None
        return ' '  # Stalemate

    def play(self, main_index, sub_index):

        if self.active_index and main_index != self.active_index:
            raise ValidationError("This is not the active board")

        if (main_index < 0 or main_index >= 9) or (sub_index < 0 or sub_index >= 9):
            raise IndexError("Invalid board index")

        if self.board[main_index] != ' ':
            raise ValueError("Board already won")

        sub_game = self.sub_games.filter(index=int(main_index)).first()

        if sub_game is None:
            raise ValueError("Invalid sub index")

        # Check if the subgrid is won or full
        if sub_game.is_game_over != None:
            # If the subgrid is over (won or stalemate), set the next active index randomly
            available_subgrids = [i for i in range(9) if self.board[i] == ' ']
            if available_subgrids:
                # Randomly pick an available subgrid
                self.set_active_index(random.choice(available_subgrids))
            else:
                # If no subgrids are available, the game is over or it's stalemate
                self.active_index = None
            return

        # Proceed with the normal play
        winner = sub_game.play(sub_index)
        sub_game.save()

        if winner is not None:
            # One downside of storing the board state as a string
            # is that you can't mutate it in place.
            board = list(self.board)
            board[main_index] = winner
            self.board = u''.join(board)
        else:
            board = list(self.board)
            board[main_index] = ' '
            self.board = u''.join(board)

        self.set_active_index(sub_index)

    def set_active_index(self, index):
        if self.board[index] != ' ':
            self.active_index = None
        else:
            self.active_index = index

  

    def play_auto(self):

        from .players import get_player

        if not self.is_game_over:
            next = self.next_player
            player = self.player_x if next == 'X' else self.player_o
            if player == 'human':
                return

            if self.active_index is None:
                open_indexes = [i for i, v in enumerate(self.board) if v == ' ']
                main_index = random.choice(open_indexes)
            else:
                main_index = self.active_index

            player_obj = get_player(player)
            sub_game = self.sub_games.filter(index=main_index).first()
            self.play(main_index, player_obj.play(sub_game))


class SubGame(models.Model):

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

        # Counter is a useful class that counts objects.
        boards = ''.join(self.game.sub_games.values_list('board', flat=True))
        count = Counter(boards)
        if count.get('X', 0) > count.get('O', 0):
            return 'O'
        return 'X'

    WINNING = [
        [0, 1, 2],  # Across top
        [3, 4, 5],  # Across middle
        [6, 7, 8],  # Across bottom
        [0, 3, 6],  # Down left
        [1, 4, 7],  # Down middle
        [2, 5, 8],  # Down right
        [0, 4, 8],  # Diagonal ltr
        [2, 4, 6],  # Diagonal rtl
    ]

    @property
    def is_game_over(self):

        board = list(self.board)
        for wins in self.WINNING:
            # Create a tuple
            w = (board[wins[0]], board[wins[1]], board[wins[2]])
            if w == ('X', 'X', 'X'):
                self.winner = 'X'
                self.save()
                return 'X'
            if w == ('O', 'O', 'O'):
                self.winner = 'O'
                self.save()
                return 'O'
        # Check for stalemate
        if ' ' in board:
            return None
        return ' '  # Stalemate or filled board

    def play(self, index):

        if index < 0 or index >= 9:
            raise IndexError("Invalid board index")

        if self.board[index] != ' ':
            raise ValueError("Square already played")

        # One downside of storing the board state as a string
        # is that you can't mutate it in place.
        board = list(self.board)
        board[index] = self.next_player
        self.board = u''.join(board)
        return self.is_game_over

    def play_auto(self):

        from .players import get_player

        if not self.is_game_over:
            next = self.next_player
            print(next)
            player = self.player_x if next == 'X' else self.player_o
            if player == 'human':
                return

            player_obj = get_player(player)
            self.play(player_obj.play(self))





