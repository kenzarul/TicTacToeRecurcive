import pygame
import numpy as np
import sys
import time

WIDTH, HEIGHT = 900, 900
ROWS, COLS = 3, 3
SQSIZE = WIDTH // COLS
LINE_WIDTH = 10
SUBLINE_WIDTH = 2
CIRC_WIDTH = 5
CROSS_WIDTH = 5
RADIUS = SQSIZE // 6
OFFSET = 20

BG_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
SUBLINE_COLOR = (150, 150, 150)
CIRC_COLOR = (255, 0, 0)
CROSS_COLOR = (0, 0, 255)
HIGHLIGHT_COLOR = (200, 200, 200)
WINNER_COLOR = (200, 200, 255)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe Récursif")
font = pygame.font.Font(None, 50)


class SubBoard:
    def __init__(self):
        self.squares = np.zeros((ROWS, COLS), dtype=int)
        self.winner = 0
        self.is_full = False

    def mark_square(self, row, col, player):
        if self.squares[row][col] == 0:
            self.squares[row][col] = player
            self.check_winner()

    def check_winner(self):
        for i in range(ROWS):
            if self.squares[i][0] == self.squares[i][1] == self.squares[i][2] != 0:
                self.winner = self.squares[i][0]
                return
            if self.squares[0][i] == self.squares[1][i] == self.squares[2][i] != 0:
                self.winner = self.squares[0][i]
                return
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            self.winner = self.squares[0][0]
            return
        if self.squares[0][2] == self.squares[1][1] == self.squares[2][0] != 0:
            self.winner = self.squares[0][2]
            return
        if np.all(self.squares != 0):
            self.is_full = True
            self.winner = 2  # Match nul

class MainBoard:
    def __init__(self):
        self.subboards = [[SubBoard() for _ in range(COLS)] for _ in range(ROWS)]
        self.main_board = np.zeros((ROWS, COLS), dtype=int)
        self.current_sub = None
        self.winner = 0

    def mark_square(self, main_row, main_col, sub_row, sub_col, player):
        subboard = self.subboards[main_row][main_col]
        subboard.mark_square(sub_row, sub_col, player)

        if subboard.winner != 0:
            self.main_board[main_row][main_col] = subboard.winner

        if self.main_board[sub_row][sub_col] == 0 and not subboard.is_full:
            self.current_sub = (sub_row, sub_col)
        else:
            self.current_sub = None

        self.check_winner()

    def check_winner(self):
        for i in range(ROWS):
            if self.main_board[i][0] == self.main_board[i][1] == self.main_board[i][2] != 0:
                self.winner = self.main_board[i][0]
                return
            if self.main_board[0][i] == self.main_board[1][i] == self.main_board[2][i] != 0:
                self.winner = self.main_board[0][i]
                return
        if self.main_board[0][0] == self.main_board[1][1] == self.main_board[2][2] != 0:
            self.winner = self.main_board[0][0]
            return
        if self.main_board[0][2] == self.main_board[1][1] == self.main_board[2][0] != 0:
            self.winner = self.main_board[0][2]
            return

class Game:
    def __init__(self):
        self.board = MainBoard()
        self.player = 1
        self.running = True
        self.last_move_time = None

    def make_move(self, main_row, main_col, sub_row, sub_col):
        if self.board.current_sub is None or self.board.current_sub == (main_row, main_col):
            subboard = self.board.subboards[main_row][main_col]
            if subboard.squares[sub_row][sub_col] == 0:
                self.board.mark_square(main_row, main_col, sub_row, sub_col, self.player)
                self.player = self.player % 2 + 1
                self.last_move_time = time.time()

    def ai_move(self):
        if self.board.current_sub:
            main_row, main_col = self.board.current_sub
        else:
            available = np.argwhere(self.board.main_board == 0)
            main_row, main_col = available[np.random.randint(len(available))]
        subboard = self.board.subboards[main_row][main_col]
        empty_cells = np.argwhere(subboard.squares == 0)
        if len(empty_cells) > 0:
            sub_row, sub_col = empty_cells[np.random.randint(len(empty_cells))]
            self.board.mark_square(main_row, main_col, sub_row, sub_col, self.player)
            self.player = self.player % 2 + 1

    def is_over(self):
        return self.board.winner != 0

    def draw(self):
        screen.fill(BG_COLOR)

        for x in range(1, COLS):
            pygame.draw.line(screen, LINE_COLOR, (x * SQSIZE, 0), (x * SQSIZE, HEIGHT), LINE_WIDTH)
            pygame.draw.line(screen, LINE_COLOR, (0, x * SQSIZE), (WIDTH, x * SQSIZE), LINE_WIDTH)

        for main_row in range(ROWS):
            for main_col in range(COLS):
                x_start = main_col * SQSIZE
                y_start = main_row * SQSIZE

                if self.board.current_sub == (main_row, main_col):
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR, (x_start, y_start, SQSIZE, SQSIZE))

                for x in range(1, COLS):
                    pygame.draw.line(screen, SUBLINE_COLOR,
                                     (x_start + x * SQSIZE // 3, y_start),
                                     (x_start + x * SQSIZE // 3, y_start + SQSIZE), SUBLINE_WIDTH)
                    pygame.draw.line(screen, SUBLINE_COLOR,
                                     (x_start, y_start + x * SQSIZE // 3),
                                     (x_start + SQSIZE, y_start + x * SQSIZE // 3), SUBLINE_WIDTH)

                subboard = self.board.subboards[main_row][main_col]
                for row in range(ROWS):
                    for col in range(COLS):
                        center_x = x_start + col * SQSIZE // 3 + SQSIZE // 6
                        center_y = y_start + row * SQSIZE // 3 + SQSIZE // 6
                        if subboard.squares[row][col] == 1:
                            pygame.draw.line(screen, CROSS_COLOR,
                                             (center_x - RADIUS, center_y - RADIUS),
                                             (center_x + RADIUS, center_y + RADIUS), CROSS_WIDTH)
                            pygame.draw.line(screen, CROSS_COLOR,
                                             (center_x + RADIUS, center_y - RADIUS),
                                             (center_x - RADIUS, center_y + RADIUS), CROSS_WIDTH)
                        elif subboard.squares[row][col] == 2:
                            pygame.draw.circle(screen, CIRC_COLOR, (center_x, center_y), RADIUS, CIRC_WIDTH)

                # Dessiner le gagnant dans la sous-grille
                if subboard.winner == 1:
                    pygame.draw.line(screen, CROSS_COLOR,
                                     (x_start + OFFSET, y_start + OFFSET),
                                     (x_start + SQSIZE - OFFSET, y_start + SQSIZE - OFFSET), CROSS_WIDTH)
                    pygame.draw.line(screen, CROSS_COLOR,
                                     (x_start + SQSIZE - OFFSET, y_start + OFFSET),
                                     (x_start + OFFSET, y_start + SQSIZE - OFFSET), CROSS_WIDTH)
                elif subboard.winner == 2:
                    pygame.draw.circle(screen, CIRC_COLOR,
                                       (x_start + SQSIZE // 2, y_start + SQSIZE // 2),
                                       SQSIZE // 3, CIRC_WIDTH)

        pygame.display.update()

def main():
    game = Game()

    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                main_row, main_col = y // SQSIZE, x // SQSIZE
                sub_row = (y % SQSIZE) // (SQSIZE // 3)
                sub_col = (x % SQSIZE) // (SQSIZE // 3)
                game.make_move(main_row, main_col, sub_row, sub_col)

        if game.player == 2 and game.running:
            if game.last_move_time and time.time() - game.last_move_time > 1:
                game.ai_move()

        game.draw()

        if game.is_over():
            print(f"Player {game.board.winner} wins!")
            game.running = False

        pygame.display.update()

main()
