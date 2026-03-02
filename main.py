"""
Match-3 Game - Pygame 

Controls:
Click + drag a tile to swap.
"""

import pygame
import random
import math

# ---------------- SETTINGS ----------------
GRID_SIZE = 8
CELL_SIZE = 64
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE + 80
SHAPE_TYPES = 5

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)

COLORS = [
    (255, 80, 80),
    (80, 200, 255),
    (80, 255, 120),
    (255, 220, 80),
    (180, 120, 255),
]

# ---------------- INIT ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Match 3 Swipe Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# ---------------- GAME DATA ----------------
grid = [[random.randint(0, SHAPE_TYPES - 1) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
score = 0

drag_start = None
selected_cell = None

# ---------- ANIMATION ----------
animating = False
anim_progress = 0
anim_tiles = None
ANIM_SPEED = 0.2

# ---------------- DRAW SHAPES ----------------
def draw_shape(surface, shape, x, y, size, color):
    cx = x + size // 2
    cy = y + size // 2
    r = size // 3

    if shape == 0:
        pygame.draw.circle(surface, color, (cx, cy), r)
    elif shape == 1:
        pygame.draw.rect(surface, color, (cx - r, cy - r, r * 2, r * 2))
    elif shape == 2:
        points = [(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)]
        pygame.draw.polygon(surface, color, points)
    elif shape == 3:
        points = [(cx, cy - r), (cx - r, cy), (cx, cy + r), (cx + r, cy)]
        pygame.draw.polygon(surface, color, points)
    elif shape == 4:
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        pygame.draw.polygon(surface, color, points)

# ---------------- DRAW GRID ----------------
def draw_grid():
    global animating, anim_progress, anim_tiles

    # normal tiles
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE + 80, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)

            if grid[y][x] is not None:
                draw_shape(screen, grid[y][x], rect.x, rect.y, CELL_SIZE, COLORS[grid[y][x]])

    # swap animation on top
    if animating and anim_tiles:
        (ax, ay), (bx, by), shapeA, shapeB = anim_tiles

        anim_progress += ANIM_SPEED

        if anim_progress >= 1:
            animating = False
            return

        offset = anim_progress

        axp = ax + (bx - ax) * offset
        ayp = ay + (by - ay) * offset

        bxp = bx + (ax - bx) * offset
        byp = by + (ay - by) * offset

        draw_shape(screen, shapeA,
                   int(axp * CELL_SIZE),
                   int(ayp * CELL_SIZE + 80),
                   CELL_SIZE, COLORS[shapeA])

        draw_shape(screen, shapeB,
                   int(bxp * CELL_SIZE),
                   int(byp * CELL_SIZE + 80),
                   CELL_SIZE, COLORS[shapeB])

# ---------------- SWAP ----------------
def swap(a, b):
    ax, ay = a
    bx, by = b
    grid[ay][ax], grid[by][bx] = grid[by][bx], grid[ay][ax]

# ---------------- MATCH DETECTION ----------------
def find_matches():
    matches = set()

    # horizontal
    for y in range(GRID_SIZE):
        count = 1
        for x in range(1, GRID_SIZE):
            if grid[y][x] == grid[y][x - 1]:
                count += 1
            else:
                if count >= 3:
                    for i in range(count):
                        matches.add((x - 1 - i, y))
                count = 1
        if count >= 3:
            for i in range(count):
                matches.add((GRID_SIZE - 1 - i, y))

    # vertical
    for x in range(GRID_SIZE):
        count = 1
        for y in range(1, GRID_SIZE):
            if grid[y][x] == grid[y - 1][x]:
                count += 1
            else:
                if count >= 3:
                    for i in range(count):
                        matches.add((x, y - 1 - i))
                count = 1
        if count >= 3:
            for i in range(count):
                matches.add((x, GRID_SIZE - 1 - i))

    return matches

# ---------------- CLEAR / GRAVITY / REFILL ----------------
def clear_matches(matches):
    global score
    for x, y in matches:
        grid[y][x] = None
    score += len(matches) * 10

def apply_gravity():
    for x in range(GRID_SIZE):
        stack = []
        for y in range(GRID_SIZE - 1, -1, -1):
            if grid[y][x] is not None:
                stack.append(grid[y][x])

        for y in range(GRID_SIZE - 1, -1, -1):
            grid[y][x] = stack.pop(0) if stack else None

def refill_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] is None:
                grid[y][x] = random.randint(0, SHAPE_TYPES - 1)

def resolve_matches():
    while True:
        matches = find_matches()
        if not matches:
            break
        clear_matches(matches)
        apply_gravity()
        refill_grid()

# remove starting matches
resolve_matches()

# ---------------- HELPER ----------------
def mouse_to_cell(pos):
    mx, my = pos
    if my < 80:
        return None
    gx = mx // CELL_SIZE
    gy = (my - 80) // CELL_SIZE
    if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
        return (gx, gy)
    return None

# ---------------- MAIN LOOP ----------------
running = True
while running:
    screen.fill(BLACK)
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # start drag
        if event.type == pygame.MOUSEBUTTONDOWN:
            drag_start = pygame.mouse.get_pos()
            selected_cell = mouse_to_cell(drag_start)

        # release drag → detect swipe
        if event.type == pygame.MOUSEBUTTONUP and selected_cell and not animating:
            end_pos = pygame.mouse.get_pos()

            dx = end_pos[0] - drag_start[0]
            dy = end_pos[1] - drag_start[1]

            if abs(dx) > 20 or abs(dy) > 20:
                sx, sy = selected_cell
                tx, ty = sx, sy

                if abs(dx) > abs(dy):
                    tx += 1 if dx > 0 else -1
                else:
                    ty += 1 if dy > 0 else -1

                if 0 <= tx < GRID_SIZE and 0 <= ty < GRID_SIZE:
                    # start animation
                    shapeA = grid[sy][sx]
                    shapeB = grid[ty][tx]

                    anim_tiles = ((sx, sy), (tx, ty), shapeA, shapeB)
                    anim_progress = 0
                    animating = True

                    swap((sx, sy), (tx, ty))

                    if find_matches():
                        resolve_matches()
                    else:
                        swap((sx, sy), (tx, ty))

            selected_cell = None

    draw_grid()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()