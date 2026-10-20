import pygame
import sys
import random

pygame.init()

GRID_SIZE = 8
CELL_SIZE = 50
BOARD_MARGIN = 50
WIDTH = GRID_SIZE * CELL_SIZE + BOARD_MARGIN * 2
HEIGHT = WIDTH + 200

BG_COLOR = (24, 24, 36)
GRID_EMPTY = (40, 44, 60)
TEXT_COLOR = (255, 255, 255)
SHAPE_COLORS = [
    (255, 75, 75), #red
    (75, 255, 75), #blue
    (75, 150, 155), #green
    (255, 200, 75), #yellow
    (200, 75, 255) #purple
]

SHAPE_TEMPLATES = [
    [[1]], #одиночный блок
    [[1, 1]], #полоска 2
    [[1, 1, 1]], #полоска 3
    [[1], [1]], #вертикаль 2
    [[1, 1, 1], [0, 1, 0]], # Т-образная
    [[1, 1], [1, 1]], #квадрат 2х2
    [[1, 1], [1, 0]], # уголок
]
board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
score = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Blast by Vodko")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 26, bold=True)


class DraggableShape:
    def __init__(self, template, color, start_x, start_y):
        self.template = template
        self.color = color
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y
        self.is_dragging = False
        self.placed = False

    def draw(self, surface):
            if self.placed:
                return
            if not isinstance(self.template, list):
                return
            for r_idx, row in enumerate(self.template):
                if not isinstance(row, list):
                    continue
                for c_idx, val in enumerate(row):
                    if val:
                        px = self.x + c_idx * (CELL_SIZE - 5)
                        py = self.y + r_idx * (CELL_SIZE - 5)
                        rect = pygame.Rect(px, py, CELL_SIZE- 7, CELL_SIZE - 7)
                        pygame.draw.rect(surface, self.color, rect, border_radius=6)

    def is_hovered(self, pos):
        h = len(self.template) * (CELL_SIZE - 5)
        w = len(self.template[0]) * (CELL_SIZE - 5)
        return self.x <= pos[0] <= self.x + w and self.y <= pos[1] <= self.y + h

    def try_place_shape(self):
        start_col = round ((self.x - BOARD_MARGIN) / CELL_SIZE)
        start_row = round ((self.y - BOARD_MARGIN) / CELL_SIZE)

        for r_idx, row in enumerate(self.template):
            if not isinstance(row, list):
                continue
            for c_idx, val  in enumerate(row):
                if val:
                    r = start_row + r_idx
                    c = start_col + c_idx
                    if r < 0 or r >= GRID_SIZE or c < 0 or c >= GRID_SIZE or board [r][c] != 0:
                        return False

        for r_idx, row in enumerate(self.template):
            for c_idx, val in enumerate(row):
                if val:
                    board [start_row + r_idx][start_col + c_idx] = self.color
        self.placed = True
        return True

def generate_shapes():
    shapes = []
    positions = [BOARD_MARGIN, WIDTH // 3 + 20, (WIDTH // 3) * 2 + 10]
    for pos_x in positions:
        tmpl = random.choice(SHAPE_TEMPLATES)
        col = random.choice (SHAPE_COLORS)
        shapes.append(DraggableShape(tmpl, col, pos_x, HEIGHT - 140))
    return shapes

current_shapes = generate_shapes()
dragged_shape = None
offset_x, offset_y = 0, 0

def draw_board():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = BOARD_MARGIN + col * CELL_SIZE
            y = BOARD_MARGIN + row * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE - 2, CELL_SIZE - 2)
            cell_val = board[row][col]
            color = cell_val if cell_val != 0 else GRID_EMPTY
            pygame.draw.rect(screen, color, rect, border_radius=6)

def check_and_clear_lines():
    global score
    rows_to_clear = []
    cols_to_clear = []

    for r in range(GRID_SIZE):
        if all (board[r][c] !=0 for c in range(GRID_SIZE)):
            rows_to_clear.append(r)

    for c in range(GRID_SIZE):
        if all(board[r][c] !=0 for r in range (GRID_SIZE)):
            cols_to_clear.append(c)

    for r in rows_to_clear:
        for c in range(GRID_SIZE):
            board [r][c] = 0

    for c in cols_to_clear:
        for r in range(GRID_SIZE):
            board [r][c] = 0

    cleared_total = len(rows_to_clear) + len(cols_to_clear)
    if cleared_total > 0:
        score += cleared_total * 100

running = True 
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for shape in current_shapes:
                    if not shape.placed and shape.is_hovered(mouse_pos):
                        dragged_shape= shape
                        dragged_shape.is_dragging = True
                        offset_x = mouse_pos[0] - shape.x
                        offset_y = mouse_pos[1] - shape.y
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragged_shape:
                if not dragged_shape.try_place_shape():
                    dragged_shape.x = dragged_shape.start_x
                    dragged_shape.y = dragged_shape.start_y
                else:
                    check_and_clear_lines()

                dragged_shape.is_dragging = False
                dragged_shape = None
                if all(s.placed for s in current_shapes):
                    current_shapes = generate_shapes()

        elif event.type == pygame.MOUSEMOTION:
            if dragged_shape and dragged_shape.is_dragging:
                dragged_shape.x = mouse_pos[0] - offset_x
                dragged_shape.y = mouse_pos[1] - offset_y

    screen.fill(BG_COLOR)
    draw_board()

    score_surface = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_surface, (BOARD_MARGIN, 15))

    for shape in current_shapes:
        shape.draw(screen)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()