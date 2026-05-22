import time
import numpy as np
from gridgame import *

##############################################################################################################################

# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.

# For your final submission, please set the GUI option to False.

# The gs argument controls the grid size. You should experiment with various sizes to ensure your code generalizes.
# Please do not modify or remove lines 18 and 19.

##############################################################################################################################

game = ShapePlacementGrid(GUI=True, render_delay_sec=0.00001, gs=6, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##############################################################################################################################

# InitializationD

# shapePos is the current position of the brush.

# currentShapeIndex is the index of the current brush type being placed (order specified in gridgame.py, and assignment instructions).

# currentColorIndex is the index of the current color being placed (order specified in gridgame.py, and assignment instructions).

# grid represents the current state of the board. 
    
    # -1 indicates an empty cell
    # 0 indicates a cell colored in the first color (indigo by default)
    # 1 indicates a cell colored in the second color (taupe by default)
    # 2 indicates a cell colored in the third color (veridian by default)
    # 3 indicates a cell colored in the fourth color (peach by default)

# placedShapes is a list of shapes that have currently been placed on the board.
    
    # Each shape is represented as a list containing three elements: a) the brush type (number between 0-8), 
    # b) the location of the shape (coordinates of top-left cell of the shape) and c) color of the shape (number between 0-3)

    # For instance [0, (0,0), 2] represents a shape spanning a single cell in the color 2=veridian, placed at the top left cell in the grid.

# done is a Boolean that represents whether coloring constraints are satisfied. Updated by the gridgames.py file.

##############################################################################################################################

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)


####################################################
# Timing your code's execution for the leaderboard.
####################################################

start = time.time()  # <- do not modify this.



##########################################
# Write all your code in the area below. 
##########################################

# AI usage: Docstring generation, code debugging, generating syntax and certain functions I wasn't sure how to implement.

import random as rand
import pygame

# Helper functions

def pump_events():
    """Let pygame process its event queue so the window doesn't freeze."""
    pygame.event.pump()

def move_brush_to(game, target_x, target_y):
    """Move the brush to (target_x, target_y) using execute commands."""
    pos, _, _, _, _, _ = game.execute('export')
    while pos[0] < target_x:
        pos, _, _, _, _, _ = game.execute('right')
    while pos[0] > target_x:
        pos, _, _, _, _, _ = game.execute('left')
    while pos[1] < target_y:
        pos, _, _, _, _, _ = game.execute('down')
    while pos[1] > target_y:
        pos, _, _, _, _, _ = game.execute('up')
    pygame.event.pump()
 
def set_shape(game, current_idx, target_idx):
    """Cycle switchshape until reaching target_idx."""
    idx = current_idx
    while idx != target_idx:
        _, idx, _, _, _, _ = game.execute('switchshape')
    pygame.event.pump()
    return idx
 
def set_color(game, current_idx, target_idx):
    """Cycle switchcolor until reaching target_idx."""
    idx = current_idx
    while idx != target_idx:
        _, _, idx, _, _, _ = game.execute('switchcolor')
    pygame.event.pump()
    return idx
 
def count_violations(grid, gs):
    """Count adjacent same-color pairs (excluding empty cells)."""
    v = 0
    for i in range(gs):
        for j in range(gs):
            c = grid[i, j]
            if c == -1:
                continue
            if j + 1 < gs and grid[i, j + 1] == c:
                v += 1
            if i + 1 < gs and grid[i + 1, j] == c:
                v += 1
    return v
 
def get_shape_cells(shape_arr, pos_x, pos_y):
    """Return list of (row, col) that a shape array would occupy at position."""
    cells = []
    for i, row in enumerate(shape_arr):
        for j, cell in enumerate(row):
            if cell:
                cells.append((pos_y + i, pos_x + j))
    return cells
 
def get_valid_color(grid, x, y, gs, num_colors=4):
    """Get a valid color for cell (row=y, col=x) that doesn't conflict with neighbors."""
    adj_colors = set()
    if x > 0: adj_colors.add(grid[y, x - 1])
    if x < gs - 1: adj_colors.add(grid[y, x + 1])
    if y > 0: adj_colors.add(grid[y - 1, x])
    if y < gs - 1: adj_colors.add(grid[y + 1, x])
    adj_colors.discard(-1)
    available = [c for c in range(num_colors) if c not in adj_colors]
    if available:
        return rand.choice(available)
    return rand.randint(0, num_colors - 1)
    
def greedy_fill(game, gs, num_colors):
    """Fill all empty cells with 1x1 shapes using valid colors."""
    _, currentShapeIndex, currentColorIndex, _, _, _ = game.execute('export')
    currentShapeIndex = set_shape(game, currentShapeIndex, 0)
    
    for row in range(gs):
        for col in range(gs):
            _, _, _, grid, _, _ = game.execute('export')
            if grid[row, col] == -1:
                color = get_valid_color(grid, col, row, gs, num_colors)
                _, _, currentColorIndex, _, _, _ = game.execute('export')
                currentColorIndex = set_color(game, currentColorIndex, color)
                move_brush_to(game, col, row)
                _, currentShapeIndex, _, _, _, _ = game.execute('export')
                if currentShapeIndex != 0:
                    currentShapeIndex = set_shape(game, currentShapeIndex, 0)
                _, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('place')

# Setup

gs = game.gridSize #6
num_colors = len(game.colors) #4
 
# Record pre-filled cells (can't undo these)
_, _, _, grid, _, _ = game.execute('export')
pre_filled = set()
for i in range(gs):
    for j in range(gs):
        if grid[i, j] != -1:
            pre_filled.add((i, j))

# Phase 1 (Greedy fill)
# Fills all empty cells using shape 0 (1x1) and chooses a color that doesn't conflict with already placed neighbors
# If violations occur from pre-filled cells, undo and retry with different random color choices

greedy_fill(game, gs, num_colors)
_, _, _, grid, placedShapes, done = game.execute('export')
print(f"After greedy fill: shapes={len(placedShapes)}, done={done}, violations={count_violations(grid, gs)}")
 
MAX_RESTARTS = 20
restarts = 0
while not done and restarts < MAX_RESTARTS:
    # Undo all agent-placed shapes
    while placedShapes:
        game.execute('undo')
        _, _, _, _, placedShapes, _ = game.execute('export')
    
    # Try again
    greedy_fill(game, gs, num_colors)
    _, _, _, grid, placedShapes, done = game.execute('export')
    restarts += 1
    print(f"Restart {restarts}: shapes={len(placedShapes)}, done={done}, violations={count_violations(grid, gs)}")

# Phase 2. First-choice hill climbing to reduce shape count
# Randomly pick a larger shape and position. If all cells it covers are the same color and are individual 1x1 placecments, undo those and place the single larger shape instead

def try_consolidate(game, pre_filled, max_iters=4000):
    shapes = game.shapes
    gs = game.gridSize
    no_improvement_count = 0
    
    for iteration in range(max_iters):
        pygame.event.pump()
        _, _, _, grid, placedShapes, done = game.execute('export')
        if not done:
            break
        
        # Pick random shape (1-8) and random position
        shape_idx = rand.randint(1, len(shapes) - 1)
        shape_arr = shapes[shape_idx]
        h, w = shape_arr.shape
        
        max_x = gs - w
        max_y = gs - h
        if max_x < 0 or max_y < 0:
            continue
        
        pos_x = rand.randint(0, max_x)
        pos_y = rand.randint(0, max_y)
        
        cells = get_shape_cells(shape_arr, pos_x, pos_y)
        
        # All cells must be same color, not pre-filled
        colors_seen = set()
        skip = False
        for (r, c) in cells:
            if (r, c) in pre_filled:
                skip = True
                break
            colors_seen.add(grid[r, c])
        if skip or len(colors_seen) != 1:
            no_improvement_count += 1
            continue
        
        target_color = colors_seen.pop()
        if target_color == -1:
            continue
        
        # Build map: cell -> index in placedShapes
        cell_to_pidx = {}
        for pidx, (si, sp, sc) in enumerate(placedShapes):
            for cell in get_shape_cells(shapes[si], sp[0], sp[1]):
                cell_to_pidx[cell] = pidx
        
        # All target cells must be covered by distinct 1x1 shapes
        pidx_set = set()
        all_single = True
        for cell in cells:
            if cell not in cell_to_pidx:
                all_single = False
                break
            pidx = cell_to_pidx[cell]
            if placedShapes[pidx][0] != 0:
                all_single = False
                break
            pidx_set.add(pidx)
        
        if not all_single or len(pidx_set) < 2:
            no_improvement_count += 1
            continue
        
        # Undo back to earliest shape we need to remove
        earliest = min(pidx_set)
        total = len(placedShapes)
        undo_depth = total - earliest
        
        if undo_depth > 40:
            no_improvement_count += 1
            continue
        
        # Save shapes to replay BEFORE undoing
        shapes_snapshot = list(placedShapes)
        shapes_to_replay = []
        for k in range(earliest, total):
            if k not in pidx_set:
                shapes_to_replay.append(shapes_snapshot[k])
        
        # Undo
        for _ in range(undo_depth):
            game.execute('undo')
        
        # Place the larger shape
        _, curSI, curCI, grid, _, _ = game.execute('export')
        curSI = set_shape(game, curSI, shape_idx)
        curCI = set_color(game, curCI, target_color)
        move_brush_to(game, pos_x, pos_y)
        
        placed_ok = False
        if game.canPlace(grid, shapes[shape_idx], [pos_x, pos_y]):
            _, curSI, curCI, grid, _, _ = game.execute('place')
            placed_ok = True
        
        # Replay kept shapes
        for (si, sp, sc) in shapes_to_replay:
            curSI = set_shape(game, curSI, si)
            curCI = set_color(game, curCI, sc)
            move_brush_to(game, sp[0], sp[1])
            if game.canPlace(grid, shapes[si], [sp[0], sp[1]]):
                _, curSI, curCI, grid, _, _ = game.execute('place')
        
        if placed_ok:
            no_improvement_count = 0
        else:
            no_improvement_count += 1
        
        if no_improvement_count > 500:
            break

_, _, _, _, _, done = game.execute('export')
if done:
    try_consolidate(game, pre_filled, max_iters=4000)

# Final state
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
print(f"\nFinal result: shapes={len(placedShapes)}, done={done}, violations={count_violations(grid, gs)}")

########################################

# Do not modify any of the code below. 

########################################

end=time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end-start))