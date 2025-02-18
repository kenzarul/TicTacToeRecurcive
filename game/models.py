# models.py
import random
from collections import Counter

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models


class Game(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    board = models.CharField(max_length=9, default=" " * 9)

    player_x = models.CharField(max_length=64, default="human")  # Human is always X
    player_o = models.CharField(max_length=64, default="computer")  # Computer is always O
    active_index = models.PositiveIntegerField(null=True, blank=True)
    winner = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f'{self.player_x} vs {self.player_o}, state="{self.board}"'

    def save(self, *args, **kwargs):
        # Ensure that player_x is always human and player_o is always computer
        self.player_x = "human"
        self.player_o = "computer"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('game:detail', kwargs={'pk': self.pk})

    @property
    def next_player(self):
        # Ensure that X is always human and O is always computer
        count = Counter(self.board)
        if count.get('X', 0) <= count.get('O', 0):
            return 'X'  # Human's turn
        return 'O'  # Computer's turn

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
        # Check if any sub-game has been won
        for sub_game in self.sub_games.all():
            if sub_game.winner:
                self.winner = sub_game.winner
                self.save()
                return self.winner

        # Check for stalemate (all sub-games are filled)
        if all(sub_game.is_game_over for sub_game in self.sub_games.all()):
            return ' '  # Stalemate

        return None  # Game is not over

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

        winner = sub_game.play(sub_index)
        sub_game.save()

        if winner is not None:
            # Update the main board with the winner of the sub-game
            board = list(self.board)
            board[main_index] = winner
            self.board = ''.join(board)
            self.save()

            # Check if the main game is over after updating the board
            if self.is_game_over:
                return f"Game finished with {self.winner} - win"

        self.set_active_index(sub_index)
        return None

    def set_active_index(self, index):
        if self.board[index] != ' ':
            self.active_index = None
        else:
            self.active_index = index

    def play_auto(self):
        """Plays for any artificial/computers players."""
        from .players import get_player

        if not self.is_game_over:
            next = self.next_player
            if next == 'O':  # Only let the computer play if it's O's turn
                player = self.player_o  # This should always be "computer"
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

    player_x = models.CharField(max_length=64, default="human")  # Human is always X
    player_o = models.CharField(max_length=64, default="computer")  # Computer is always O
    winner = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"Game {self.game.pk} - Index {self.index}"

    def save(self, *args, **kwargs):
        # Ensure that player_x is always human and player_o is always computer
        self.player_x = "human"
        self.player_o = "computer"
        super().save(*args, **kwargs)

    @property
    def next_player(self):
        # Ensure that X is always human and O is always computer
        count = Counter(self.board)
        if count.get('X', 0) <= count.get('O', 0):
            return 'X'  # Human's turn
        return 'O'  # Computer's turn

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

    def play(self, index):
        if index < 0 or index >= 9:
            raise IndexError("Invalid board index")

        if self.board[index] != ' ':
            raise ValueError("Square already played")

        board = list(self.board)
        board[index] = self.next_player
        self.board = ''.join(board)
        return self.is_game_over

    def play_auto(self):
        from .players import get_player

        if not self.is_game_over:
            next = self.next_player
            if next == 'O':  # Only let the computer play if it's O's turn
                player = self.player_o  # This should always be "computer"
                if player == 'human':
                    return

                player_obj = get_player(player)
                self.play(player_obj.play(self))
