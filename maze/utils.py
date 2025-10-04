# utils.py
import time


BACKGROUND_COLOR = "#F0F0F0"

START_COLOR = "#00FF00"
END_COLOR = "#FF0000"
BUTTON_COLOR = "#DDDDDD"
WALL_COLOR = "#000A38"

DIRS_4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIRS_8 = [
    (-1, 0), (1, 0), (0, -1), (0, 1),
    (-1, -1), (-1, 1), (1, -1), (1, 1)
]



def draw_cell(canvas, rectangles, r, c, color):
    canvas.itemconfig(rectangles[r][c], fill=color)

def reset_canvas_colors(rows, cols, rectangles, canvas, start, end, skip_colors=(WALL_COLOR, START_COLOR, END_COLOR)):
    for r in range(rows):
        for c in range(cols):
            pos = (r, c)
            current_color = canvas.itemcget(rectangles[r][c], "fill")
            if pos != start and pos != end and current_color not in skip_colors:
                draw_cell(canvas, rectangles, r, c, BACKGROUND_COLOR)
            canvas.itemconfig(rectangles[r][c], outline="", width=0)
    canvas.update()

def is_in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def chebyshev_distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def delay_step(canvas, delay_var):
    canvas.update()
    delay = delay_var.get() / 1000
    if delay > 0:
        time.sleep(delay)

        