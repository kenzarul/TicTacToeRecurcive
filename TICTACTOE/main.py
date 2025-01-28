import pygame
import numpy as np
import sys
import time
WIDTH, HEIGHT = 800, 800
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
CIRC_COLOR = (255, 0, 0)     # O en rouge
CROSS_COLOR = (0, 0, 255)    # X en bleu
HIGHLIGHT_COLOR = (200, 200, 200)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe Récursif")


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
        # Vérification lignes
        for i in range(ROWS):
            if self.squares[i][0] == self.squares[i][1] == self.squares[i][2] != 0:
                self.winner = self.squares[i][0]
                return

        # Vérification colonnes
        for j in range(COLS):
            if self.squares[0][j] == self.squares[1][j] == self.squares[2][j] != 0:
                self.winner = self.squares[0][j]
                return

        # Vérification diagonales
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            self.winner = self.squares[0][0]
            return
        if self.squares[0][2] == self.squares[1][1] == self.squares[2][0] != 0:
            self.winner = self.squares[0][2]
            return

        # Si sous-grille pleine => nul
        if np.all(self.squares != 0):
            self.is_full = True
            self.winner = 3


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
        if (self.main_board[sub_row][sub_col] == 0) and (not subboard.is_full):
            self.current_sub = (sub_row, sub_col)
        else:
            self.current_sub = None
        self.check_winner()

    def check_winner(self):
        for i in range(ROWS):
            if self.main_board[i][0] == self.main_board[i][1] == self.main_board[i][2] != 0:
                self.winner = self.main_board[i][0]
                return
        for j in range(COLS):
            if self.main_board[0][j] == self.main_board[1][j] == self.main_board[2][j] != 0:
                self.winner = self.main_board[0][j]
                return
        if self.main_board[0][0] == self.main_board[1][1] == self.main_board[2][2] != 0:
            self.winner = self.main_board[0][0]
            return
        if self.main_board[0][2] == self.main_board[1][1] == self.main_board[2][0] != 0:
            self.winner = self.main_board[0][2]
            return
        all_done = True
        for i in range(ROWS):
            for j in range(COLS):
                if self.subboards[i][j].winner == 0:
                    all_done = False
                    break
        if all_done:
            self.winner = 3

class Game:
    def __init__(self, difficulty):
        self.board = MainBoard()
        self.player = 1
        self.running = True
        self.last_move_time = None
        self.difficulty = difficulty

    def make_move(self, main_row, main_col, sub_row, sub_col):
        if self.board.current_sub is None or self.board.current_sub == (main_row, main_col):
            subboard = self.board.subboards[main_row][main_col]
            if subboard.squares[sub_row][sub_col] == 0:
                self.board.mark_square(main_row, main_col, sub_row, sub_col, self.player)
                self.player = 1 if self.player == 2 else 2
                self.last_move_time = time.time()

    def ai_move(self):
        if self.difficulty == 0:
            self.ai_random_move()
        elif self.difficulty == 1:
            if not self.ai_win_or_block():
                self.ai_random_move()
        elif self.difficulty == 2:
            move = self.minimax_decision()
            if move is not None:
                (mr, mc, sr, sc) = move
                self.board.mark_square(mr, mc, sr, sc, self.player)
                self.player = 1 if self.player == 2 else 2

    def ai_random_move(self):
        possible_subs = []
        if self.board.current_sub:
            (mr, mc) = self.board.current_sub
            if self.board.main_board[mr][mc] == 0:
                possible_subs.append((mr, mc))
        else:
            for r in range(3):
                for c in range(3):
                    if self.board.main_board[r][c] == 0:
                        possible_subs.append((r, c))

        if not possible_subs:
            return

        (mr, mc) = possible_subs[np.random.randint(len(possible_subs))]
        subb = self.board.subboards[mr][mc]
        empty_cells = np.argwhere(subb.squares == 0)
        if len(empty_cells) > 0:
            (sr, sc) = empty_cells[np.random.randint(len(empty_cells))]
            self.board.mark_square(mr, mc, sr, sc, self.player)
            self.player = 1 if self.player == 2 else 2

    def ai_win_or_block(self):
        if self.ai_immediate_move(self.player):
            return True
        adv = 1 if self.player == 2 else 2
        if self.ai_immediate_move(adv):
            return True
        return False

    def ai_immediate_move(self, target_player):
        possible_subs = []
        if self.board.current_sub:
            (r, c) = self.board.current_sub
            if self.board.main_board[r][c] == 0:
                possible_subs.append((r, c))
        else:
            for r in range(3):
                for c in range(3):
                    if self.board.main_board[r][c] == 0:
                        possible_subs.append((r, c))

        for (mr, mc) in possible_subs:
            subb = self.board.subboards[mr][mc]
            if subb.winner == 0:
                for sr in range(3):
                    for sc in range(3):
                        if subb.squares[sr][sc] == 0:
                            subb.squares[sr][sc] = target_player
                            subb.check_winner()

                            if subb.winner == target_player:
                                subb.squares[sr][sc] = 0
                                subb.winner = 0
                                self.board.mark_square(mr, mc, sr, sc, self.player)
                                self.player = 1 if self.player == 2 else 2
                                return True
                            else:
                                subb.squares[sr][sc] = 0
                                subb.winner = 0
        return False

    def minimax_decision(self):
        best_score = -9999
        best_move = None
        moves = self.get_all_possible_moves(self.player)
        if not moves:
            return None

        for move in moves:
            (mr, mc, sr, sc) = move
            saved_squares = np.copy(self.board.subboards[mr][mc].squares)
            saved_winner = self.board.subboards[mr][mc].winner
            saved_main = np.copy(self.board.main_board)
            saved_sub = self.board.current_sub
            saved_global_winner = self.board.winner
            self.board.mark_square(mr, mc, sr, sc, self.player)

            score = self.minimax(0, False, alpha=-9999, beta=9999, max_depth=4)
            self.board.subboards[mr][mc].squares = saved_squares
            self.board.subboards[mr][mc].winner = saved_winner
            self.board.main_board = saved_main
            self.board.current_sub = saved_sub
            self.board.winner = saved_global_winner

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, depth, is_maximizing, alpha, beta, max_depth=4):
        if self.board.winner == 2:  # O gagne
            return +1
        if self.board.winner == 1:  # X gagne
            return -1
        if self.board.winner == 3:  # nul
            return 0
        if depth == max_depth:
            return self.heuristic_evaluation()

        current_player = 2 if is_maximizing else 1
        moves = self.get_all_possible_moves(current_player)
        if not moves:
            return 0

        if is_maximizing:
            best_eval = -9999
            for move in moves:
                (mr, mc, sr, sc) = move
                saved_squares = np.copy(self.board.subboards[mr][mc].squares)
                saved_winner = self.board.subboards[mr][mc].winner
                saved_main = np.copy(self.board.main_board)
                saved_sub = self.board.current_sub
                saved_global_winner = self.board.winner
                self.board.mark_square(mr, mc, sr, sc, current_player)
                eval_score = self.minimax(depth+1, False, alpha, beta, max_depth)
                self.board.subboards[mr][mc].squares = saved_squares
                self.board.subboards[mr][mc].winner = saved_winner
                self.board.main_board = saved_main
                self.board.current_sub = saved_sub
                self.board.winner = saved_global_winner

                best_eval = max(best_eval, eval_score)
                alpha = max(alpha, best_eval)
                if beta <= alpha:
                    break

            return best_eval
        else:
            worst_eval = 9999
            for move in moves:
                (mr, mc, sr, sc) = move
                saved_squares = np.copy(self.board.subboards[mr][mc].squares)
                saved_winner = self.board.subboards[mr][mc].winner
                saved_main = np.copy(self.board.main_board)
                saved_sub = self.board.current_sub
                saved_global_winner = self.board.winner

                self.board.mark_square(mr, mc, sr, sc, current_player)
                eval_score = self.minimax(depth+1, True, alpha, beta, max_depth)
                self.board.subboards[mr][mc].squares = saved_squares
                self.board.subboards[mr][mc].winner = saved_winner
                self.board.main_board = saved_main
                self.board.current_sub = saved_sub
                self.board.winner = saved_global_winner

                worst_eval = min(worst_eval, eval_score)
                beta = min(beta, worst_eval)
                if beta <= alpha:
                    break

            return worst_eval

    def get_all_possible_moves(self, player):
        moves = []
        if self.board.current_sub:
            (mr, mc) = self.board.current_sub
            if self.board.main_board[mr][mc] == 0:
                subb = self.board.subboards[mr][mc]
                if subb.winner == 0:
                    empty_cells = np.argwhere(subb.squares == 0)
                    for (sr, sc) in empty_cells:
                        moves.append((mr, mc, sr, sc))
        else:
            for mr in range(3):
                for mc in range(3):
                    if self.board.main_board[mr][mc] == 0:
                        subb = self.board.subboards[mr][mc]
                        if subb.winner == 0:
                            empty_cells = np.argwhere(subb.squares == 0)
                            for (sr, sc) in empty_cells:
                                moves.append((mr, mc, sr, sc))

        return moves

    def heuristic_evaluation(self):
        score = 0

        scoring_map = {
            (3, 0): 1000,
            (2, 0): 50,
            (1, 0): 5,
            (0, 3): -1000,
            (0, 2): -50,
            (0, 1): -5
        }

        for mr in range(3):
            for mc in range(3):
                subb = self.board.subboards[mr][mc]
                squares = subb.squares

                if subb.winner == 2:
                    score += 200
                    continue
                elif subb.winner == 1:
                    score -= 200
                    continue
                elif subb.winner == 3:
                    continue
                for i in range(3):
                    row = squares[i, :]
                    O_count = np.count_nonzero(row == 2)
                    X_count = np.count_nonzero(row == 1)
                    pts = scoring_map.get((O_count, X_count), 0)
                    score += pts
                    col = squares[:, i]
                    O_count = np.count_nonzero(col == 2)
                    X_count = np.count_nonzero(col == 1)
                    pts = scoring_map.get((O_count, X_count), 0)
                    score += pts

                diag_main = squares[[0,1,2],[0,1,2]]
                O_count = np.count_nonzero(diag_main == 2)
                X_count = np.count_nonzero(diag_main == 1)
                pts = scoring_map.get((O_count, X_count), 0)
                score += pts

                diag_sec = squares[[0,1,2],[2,1,0]]
                O_count = np.count_nonzero(diag_sec == 2)
                X_count = np.count_nonzero(diag_sec == 1)
                pts = scoring_map.get((O_count, X_count), 0)
                score += pts

        return score
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
                    pygame.draw.line(
                        screen, SUBLINE_COLOR,
                        (x_start + x * SQSIZE // 3, y_start),
                        (x_start + x * SQSIZE // 3, y_start + SQSIZE),
                        SUBLINE_WIDTH
                    )
                    pygame.draw.line(
                        screen, SUBLINE_COLOR,
                        (x_start, y_start + x * SQSIZE // 3),
                        (x_start + SQSIZE, y_start + x * SQSIZE // 3),
                        SUBLINE_WIDTH
                    )

                subb = self.board.subboards[main_row][main_col]
                for row in range(3):
                    for col in range(3):
                        center_x = x_start + col * SQSIZE // 3 + SQSIZE // 6
                        center_y = y_start + row * SQSIZE // 3 + SQSIZE // 6
                        val = subb.squares[row][col]
                        if val == 1:
                            pygame.draw.line(
                                screen, CROSS_COLOR,
                                (center_x - RADIUS, center_y - RADIUS),
                                (center_x + RADIUS, center_y + RADIUS),
                                CROSS_WIDTH
                            )
                            pygame.draw.line(
                                screen, CROSS_COLOR,
                                (center_x + RADIUS, center_y - RADIUS),
                                (center_x - RADIUS, center_y + RADIUS),
                                CROSS_WIDTH
                            )
                        elif val == 2:
                            pygame.draw.circle(screen, CIRC_COLOR, (center_x, center_y), RADIUS, CIRC_WIDTH)

                if subb.winner == 1:
                    pygame.draw.line(
                        screen, CROSS_COLOR,
                        (x_start + OFFSET, y_start + OFFSET),
                        (x_start + SQSIZE - OFFSET, y_start + SQSIZE - OFFSET),
                        CROSS_WIDTH
                    )
                    pygame.draw.line(
                        screen, CROSS_COLOR,
                        (x_start + SQSIZE - OFFSET, y_start + OFFSET),
                        (x_start + OFFSET, y_start + SQSIZE - OFFSET),
                        CROSS_WIDTH
                    )
                elif subb.winner == 2:
                    pygame.draw.circle(
                        screen, CIRC_COLOR,
                        (x_start + SQSIZE // 2, y_start + SQSIZE // 2),
                        SQSIZE // 3, CIRC_WIDTH
                    )

        pygame.display.update()


def main():
    difficulty_str = input("Choisissez la difficulté (0=Facile, 1=Moyen, 2=Difficile) : ")
    try:
        difficulty = int(difficulty_str)
    except ValueError:
        difficulty = 0

    game = Game(difficulty)

    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game.is_over():
                if game.player == 1:
                    x, y = event.pos
                    main_row = y // SQSIZE
                    main_col = x // SQSIZE
                    sub_row = (y % SQSIZE) // (SQSIZE // 3)
                    sub_col = (x % SQSIZE) // (SQSIZE // 3)
                    game.make_move(main_row, main_col, sub_row, sub_col)
        if not game.is_over() and game.player == 2:
            if game.last_move_time and time.time() - game.last_move_time > 0.3:
                game.ai_move()

        game.draw()
        if game.is_over():
            print("Partie terminée.")
            if game.board.winner == 1:
                print("Le joueur X (1) gagne !")
            elif game.board.winner == 2:
                print("Le joueur O (2) gagne !")
            else:
                print("Match nul !")
            pygame.time.wait(2000)
            game.running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
