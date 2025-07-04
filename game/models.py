import random
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
class GameHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    result = models.CharField(max_length=10, choices=[("win", "Win"), ("loss", "Loss"), ("draw", "Draw")])
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.result} - {self.date_created}"

class Game(models.Model):
    room_code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    last_main_index = models.PositiveIntegerField(null=True, blank=True)
    last_sub_index = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    board = models.CharField(max_length=9, default=" " * 9)
    player_x = models.CharField(max_length=255, null=True, blank=True)
    player_o = models.CharField(max_length=255, null=True, blank=True)
    active_index = models.PositiveIntegerField(null=True, blank=True)
    winner = models.CharField(max_length=64, null=True, blank=True)
    last_player = models.CharField(max_length=1, null=True, blank=True)

    # Timer fields
    time_x = models.IntegerField(default=300)
    time_o = models.IntegerField(default=300)
    remaining_x = models.IntegerField(default=300)
    remaining_o = models.IntegerField(default=300)
    last_move_time = models.DateTimeField(null=True, blank=True)

    WINNING = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ]

    def __str__(self):
        return f"{self.player_x} vs {self.player_o} | {self.room_code}"

    def get_absolute_url(self):
        return reverse('game:detail', kwargs={'pk': self.pk})

    @property
    def next_player(self):
        return 'O' if self.last_player == 'X' else 'X'

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
        return None if ' ' in board else ' '

    def play(self, main_index, sub_index, symbol=None):
        if self.winner:
            raise ValidationError("Game is already over")

        if symbol is None:
            symbol = self.next_player

        now = timezone.now()
        if self.last_move_time:
            elapsed = int((now - self.last_move_time).total_seconds())
            if self.last_player == 'X':
                self.remaining_x = max(0, self.remaining_x - elapsed)
                if self.remaining_x <= 0:
                    self.winner = 'O'
                    self.save()
                    return self.winner
            elif self.last_player == 'O':
                self.remaining_o = max(0, self.remaining_o - elapsed)
                if self.remaining_o <= 0:
                    self.winner = 'X'
                    self.save()
                    return self.winner
        self.last_move_time = now

        if self.active_index is not None and main_index != self.active_index:
            raise ValidationError("This is not the active board")
        if main_index < 0 or main_index >= 9 or sub_index < 0 or sub_index >= 9:
            raise IndexError("Invalid board index")
        if self.board[main_index] != ' ':
            return None

        sub_game = self.sub_games.filter(index=main_index).first()
        if not sub_game:
            raise ValueError("SubGame does not exist")

        if sub_game.is_game_over or ' ' not in sub_game.board:
            raise ValidationError("This sub-board is full or already won")

        # Extract the winner and winning_line from the SubGame play method
        winner, winning_line = sub_game.play(sub_index, symbol)
        sub_game.save()

        self.last_main_index = main_index
        self.last_sub_index = sub_index
        self.last_player = symbol

        if winner:
            self.board = self.board[:main_index] + winner + self.board[main_index + 1:]
        elif ' ' not in sub_game.board:
            self.board = self.board[:main_index] + ' ' + self.board[main_index + 1:]

        self.set_active_index(sub_index)
        self.save()
        self.is_game_over  # Trigger win check
        return winner

    def set_active_index(self, index):
        """
        Set the active subgame index for the next move.
        """
        if index is None or self.board[index] != ' ':
            self.active_index = None
        else:
            sub_game = self.sub_games.filter(index=index).first()
            if not sub_game or sub_game.is_game_over or ' ' not in sub_game.board:
                self.active_index = None
            else:
                self.active_index = index

    def create_subgames(self):
        if not self.player_x or not self.player_o:
            raise ValueError("Cannot create subgames without both player_x and player_o")
        self.sub_games.all().delete()
        for i in range(9):
            SubGame.objects.create(
                game=self,
                index=i,
                player_x=self.player_x,
                player_o=self.player_o
            )
        self.board = " " * 9
        self.last_player = None
        # Initialize remaining time from time_x and time_o
        self.remaining_x = self.time_x
        self.remaining_o = self.time_o
        self.last_move_time = timezone.now()
        self.winner = None
        self.active_index = None
        self.save()

    def reset_state(self):
        """
        Reset the game state to its initial configuration.
        """
        self.board = " " * 9
        self.last_main_index = None
        self.last_sub_index = None
        self.winner = None
        self.last_player = None
        self.active_index = None
        self.remaining_x = self.time_x
        self.remaining_o = self.time_o
        self.last_move_time = None
        self.sub_games.all().delete()
        for i in range(9):
            SubGame.objects.create(
                game=self,
                index=i,
                player_x=self.player_x,
                player_o=self.player_o
            )
        self.save()
        self.refresh_from_db()  # Ensure in-memory state is fresh

    def play_auto(self):
        if not self.is_game_over:
            next_symbol = self.next_player
            player = self.player_x if next_symbol == 'X' else self.player_o
            if player == 'human':
                return
            from game.players import get_player
            player_obj = get_player(player)
            main_index = self.active_index if self.active_index is not None else random.choice(
                [i for i, v in enumerate(self.board) if v == ' '])
            sub_game = self.sub_games.filter(index=main_index).first()
            sub_index = player_obj.play(sub_game, next_symbol)
            self.play(main_index, sub_index, next_symbol)

    def play(self, main_index, sub_index, symbol=None):
        """
        Handle a move in the game.
        """
        if self.winner:
            raise ValidationError("Game is already over")

        if symbol is None:
            symbol = self.next_player

        now = timezone.now()
        if self.last_move_time:
            elapsed = int((now - self.last_move_time).total_seconds())
            if self.last_player == 'X':
                self.remaining_x = max(0, self.remaining_x - elapsed)
                if self.remaining_x <= 0:
                    self.winner = 'O'
                    self.save()
                    return self.winner
            elif self.last_player == 'O':
                self.remaining_o = max(0, self.remaining_o - elapsed)
                if self.remaining_o <= 0:
                    self.winner = 'X'
                    self.save()
                    return self.winner
        self.last_move_time = now

        if self.active_index is not None and main_index != self.active_index:
            raise ValidationError("This is not the active board")
        if main_index < 0 or main_index >= 9 or sub_index < 0 or sub_index >= 9:
            raise IndexError("Invalid board index")
        if self.board[main_index] != ' ':
            return None

        sub_game = self.sub_games.filter(index=main_index).first()
        if not sub_game:
            raise ValueError("SubGame does not exist")

        if sub_game.is_game_over or ' ' not in sub_game.board:
            raise ValidationError("This sub-board is full or already won")

        # Extract the winner and winning_line from the SubGame play method
        winner, winning_line = sub_game.play(sub_index, symbol)
        sub_game.save()

        self.last_main_index = main_index
        self.last_sub_index = sub_index
        self.last_player = symbol

        if winner:
            self.board = self.board[:main_index] + winner + self.board[main_index + 1:]
        elif ' ' not in sub_game.board:
            self.board = self.board[:main_index] + ' ' + self.board[main_index + 1:]

        self.set_active_index(sub_index)
        self.save()
        self.is_game_over  # Trigger win check
        return winner

    def set_active_index(self, index):
        """
        Set the active subgame index for the next move.
        """
        if index is None or self.board[index] != ' ':
            self.active_index = None
        else:
            sub_game = self.sub_games.filter(index=index).first()
            if not sub_game or sub_game.is_game_over or ' ' not in sub_game.board:
                self.active_index = None
            else:
                self.active_index = index

    def create_subgames(self):
        if not self.player_x or not self.player_o:
            raise ValueError("Cannot create subgames without both player_x and player_o")
        self.sub_games.all().delete()
        for i in range(9):
            SubGame.objects.create(
                game=self,
                index=i,
                player_x=self.player_x,
                player_o=self.player_o
            )
        self.board = " " * 9
        self.last_player = None
        # Initialize remaining time from time_x and time_o
        self.remaining_x = self.time_x
        self.remaining_o = self.time_o
        self.last_move_time = timezone.now()
        self.winner = None
        self.active_index = None
        self.save()

    def reset_state(self):
        """
        Reset the game state to its initial configuration.
        """
        self.board = " " * 9
        self.last_main_index = None
        self.last_sub_index = None
        self.winner = None
        self.last_player = None
        self.active_index = None
        self.remaining_x = self.time_x
        self.remaining_o = self.time_o
        self.last_move_time = None
        self.sub_games.all().delete()
        for i in range(9):
            SubGame.objects.create(
                game=self,
                index=i,
                player_x=self.player_x,
                player_o=self.player_o
            )
        self.save()
        self.refresh_from_db()  # Ensure in-memory state is fresh


class SubGame(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sub_games')
    index = models.PositiveIntegerField()
    board = models.CharField(max_length=9, default=" " * 9)
    player_x = models.CharField(max_length=255, null=True, blank=True)
    player_o = models.CharField(max_length=255, null=True, blank=True)
    winner = models.CharField(max_length=64, null=True, blank=True)
    last_move_index = models.PositiveIntegerField(null=True, blank=True)
    last_computer_move = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    WINNING = Game.WINNING

    def __str__(self):
        return f"SubGame {self.game.pk}-{self.index}"

    def get_winning_line(self):
        board = list(self.board)
        for wins in self.WINNING:
            w = (board[wins[0]], board[wins[1]], board[wins[2]])
            if w == ('X', 'X', 'X') or w == ('O', 'O', 'O'):
                return wins
        return None

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
        return None if ' ' in board else ' '

    def play(self, index, symbol):
        if index < 0 or index >= 9:
            raise IndexError("Invalid board index")
        if self.board[index] != ' ':
            raise ValueError("Square already played")

        board = list(self.board)
        board[index] = symbol
        self.board = ''.join(board)

        self.last_move_index = index
        self.save()
        winner = self.is_game_over
        winning_line = None
        if winner in ('X', 'O'):
            winning_line = self.get_winning_line()
        return (winner, winning_line)

    def play_auto(self):
        if not self.is_game_over:
            next_symbol = 'O' if self.board.count('X') > self.board.count('O') else 'X'
            player = self.player_x if next_symbol == 'X' else self.player_o
            if player == 'human':
                return
            from game.players import get_player
            player_obj = get_player(player)
            sub_index = player_obj.play(self, next_symbol)
            self.play(sub_index, next_symbol)
            self.last_move_index = sub_index
            self.save()