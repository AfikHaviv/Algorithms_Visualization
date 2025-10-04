import sys
import tkinter as tk 
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import customtkinter as ctk
import random
import time
from time import perf_counter
from maze.utils import reset_canvas_colors, DIRS_4, DIRS_8, manhattan_distance, chebyshev_distance
from maze.algorithms import bfs, a_star, bidirectional_bfs, dfs, jps

sys.setrecursionlimit(5000)

#Size constants for the maze grid
CELL_SIZE = 10
GRID_ROWS = 81
GRID_COLS = 77

SEARCH_COLOR = "#26BEFA"
PATH_COLOR = "#E3FC00"

START_COLOR = "#00FF00"
END_COLOR = "#FF0000"
WALL_COLOR = "#000A38"
BUTTON_COLOR = "#DDDDDD"
BACKGROUND_COLOR = "#F0F0F0"


class MazeGUI:
    """A GUI for visualizing the maze."""
    def __init__(self, root, visited_label=None, path_label=None, time_label=None, best_label=None, algorithm_buttons = None, result_label=None):

        self.root = root
        self.start_cell = None 
        self.end_cell = None 
        self.drawing_wall = False
        self.stop_requested = False
        self.is_running = False
        self.was_run = False
        self.generated_maze = False
        self.delay_value = tk.DoubleVar(value=5)
        self.algorithm_buttons = algorithm_buttons
        self.move_mode = tk.StringVar(value="4")
        self.run_token = 0

        self.paused = False
        self.overlay_drawings = []
        self._overlay_prev = None
        self.OVERLAY_COLOR = "#FF4040"


        self.visited_label = visited_label
        self.path_label = path_label
        self.time_label = time_label
        self.result_label = result_label

        self.best_time = None
        self.fastest_algo = None
        self.best_label = best_label

        self._pause_total = 0.0
        self._pause_started_at = None


        self.canvas = tk.Canvas(root, width=GRID_COLS * CELL_SIZE, height=GRID_ROWS * CELL_SIZE)
        self.canvas.pack()
    
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.rectangles = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        self.draw_grid()

        self.canvas.bind("<ButtonPress-1>", self.on_left_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)

    def draw_grid(self): 
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=BACKGROUND_COLOR, outline="")
                
                self.rectangles[row][col] = rect

    def on_right_click(self, event):
        if self.paused:
            return
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if self.is_running:
            messagebox.showinfo("Error", "Cannot change start and end while an algorithm is running, try to reset run")
            return 
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
           if self.grid[row][col] == 1:
                messagebox.showinfo("Error", "Cannot set start and end on a wall")
                return 
           
           if self.start_cell is None:
               self.start_cell = (row, col)
               self.canvas.itemconfig(self.rectangles[row][col], fill=START_COLOR)
           elif self.end_cell is None:
                self.end_cell = (row, col)
                self.canvas.itemconfig(self.rectangles[row][col], fill=END_COLOR)
           else:
               s_row, s_col = self.start_cell
               e_row, e_col = self.end_cell
               self.canvas.itemconfig(self.rectangles[s_row][s_col], fill=BACKGROUND_COLOR)
               self.canvas.itemconfig(self.rectangles[e_row][e_col], fill=BACKGROUND_COLOR)
               self.start_cell = (row, col)
               self.end_cell = None
               self.canvas.itemconfig(self.rectangles[row][col], fill=START_COLOR)
           if self.start_cell == self.end_cell: # Cannot set start and end on same cell
               self.end_cell = None
               self.canvas.itemconfig(self.rectangles[row][col], fill=START_COLOR)
               messagebox.showinfo("Error", "Cannot set start and end on same spot")
               return

    def on_left_press(self, event):
        if self.paused:
            return
        if self.is_running:
            messagebox.showinfo("Error", "Cannot change maze while an algorithem is running, try to reset run")
            return 
        self.drawing_wall = True
        self.toggle_wall(event)
        
    def on_mouse_drag(self, event):
        if self.paused:
            return
        if self.drawing_wall:
            self.draw_wall(event)
    
    def on_left_release(self,event):
        if self.paused:
            return
        self.drawing_wall = False

    def modify_wall(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            if (row, col) == self.start_cell or (row, col) == self.end_cell:
                return
            
            if self.grid[row][col] == 0:
                self.grid[row][col] = 1
                self.canvas.itemconfig(self.rectangles[row][col], fill=WALL_COLOR)
            
    def toggle_wall(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            if (row, col) == self.start_cell or (row, col) == self.end_cell:
                return
            
            if self.grid[row][col] == 1:
                self.grid[row][col] = 0
                self.canvas.itemconfig(self.rectangles[row][col], fill=BACKGROUND_COLOR)
            else:
                self.grid[row][col] = 1
                self.canvas.itemconfig(self.rectangles[row][col], fill=WALL_COLOR)

    def draw_wall(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        self.generated_maze = False

        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            if (row, col) == self.start_cell or (row, col) == self.end_cell:
                return
            
            if self.grid[row][col] == 0:
                self.grid[row][col] = 1
                self.canvas.itemconfig(self.rectangles[row][col], fill=WALL_COLOR)

    def highlight_button(self, name):
        self.reset_button_colors()
        button = self.algorithm_buttons.get(name)
        if button:
            button.configure(fg_color="#1d9711", hover_color="#34dd42")
    
    def reset_button_colors(self):
        for button in self.algorithm_buttons.values():
            button.configure(fg_color="#1f6aa5", hover_color= "#144870")
    
    def make_pause_wait(self):
        def pause_wait():
            while self.paused and not self.stop_requested:
                try:
                    self.canvas.update()
                except Exception:
                    break
                time.sleep(0.01)
        return pause_wait

    def overlay_left_press(self, event):
        self._overlay_prev = (event.x, event.y)

    def overlay_mouse_drag(self, event):
        if self._overlay_prev is None:
            self._overlay_prev = (event.x, event.y)
            return
        x0, y0 = self._overlay_prev
        x1, y1 = event.x, event.y
        line_id = self.canvas.create_line(x0, y0, x1, y1, fill=self.OVERLAY_COLOR, width=4)
        self.overlay_drawings.append(line_id)
        self._overlay_prev = (x1, y1)

    def overlay_left_release(self, event):
        self._overlay_prev = None

    def _pause_start(self):
        if self._pause_started_at is None:
            self._pause_started_at = perf_counter()

    def _pause_end(self):
        try:
            if self._pause_started_at is not None:
                self._pause_total += perf_counter() - self._pause_started_at
                self._pause_started_at = None
        except Exception:
            self._pause_started_at = None

    def toggle_pause(self):
        if not (self.paused or self.is_running):
            messagebox.showinfo("Info", "No algorithm is running.")
            return

        self.paused = not self.paused 

        if self.paused:
            self._pause_start()
            self.canvas.bind("<ButtonPress-1>", self.overlay_left_press)
            self.canvas.bind("<B1-Motion>", self.overlay_mouse_drag)
            self.canvas.bind("<ButtonRelease-1>", self.overlay_left_release)
            for algo in self.algorithm_buttons.values():
                    algo.configure(state="normal")
            if hasattr(self, "pause_btn"):
                self.pause_btn.configure(text="Resume Run (space)")
        else:
            self._pause_end()
            for item_id in self.overlay_drawings:
                self.canvas.delete(item_id)
            self.overlay_drawings.clear()
            self._overlay_prev = None
            if self.is_running:
                for algo in self.algorithm_buttons.values():
                        algo.configure(state="disabled")
            self.canvas.bind("<ButtonPress-1>", self.on_left_press)
            self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
            if hasattr(self, "pause_btn"):
                self.pause_btn.configure(text="Pause Run (space)")

    def run_search(self, algorithm="BFS"):
        if self.was_run:
            self.reset_algorithm_visuals()

        if self.result_label:
            self.result_label.configure(text="Result: Searching...")

        dirs = DIRS_8 if self.move_mode.get() == "8" else DIRS_4
        heuristic = manhattan_distance if self.move_mode.get() == "4" else chebyshev_distance

        self.stop_requested = False
        self.is_running = True
        self.was_run = True
        try:
            if hasattr(self, "move_toggle"):
                self.move_toggle.configure(state="disabled")
            for algo in self.algorithm_buttons.values():
                algo.configure(state="disabled")
        except Exception:
            pass

        self._pause_total = 0.0
        self._pause_started_at = None

        if self.paused:
            self.paused = False

        self.run_token += 1
        my_token = self.run_token 
        def stop_flag():
            return self.stop_requested or (self.run_token != my_token)

        if self.start_cell is None or self.end_cell is None:
            messagebox.showwarning("Error", "Start or end cell not set.")
            self.is_running = False
            self.was_run = False
            try:
                if hasattr(self, "move_toggle"):
                    self.move_toggle.configure(state="normal")
                for algo in self.algorithm_buttons.values():
                    algo.configure(state="normal")
            except Exception:
                pass
            return

        pause_wait = self.make_pause_wait()

        start_time = perf_counter()
        visited = 0
        path_length = 0
        result = None

        self.highlight_button(algorithm)

        if algorithm == "BFS":
            result = bfs(self.grid, self.start_cell, self.end_cell, self.rectangles,
                        self.canvas, stop_flag, self.delay_value, dirs, pause_wait)
        elif algorithm == "A*":
            result = a_star(self.grid, self.start_cell, self.end_cell, self.rectangles,
                            self.canvas, stop_flag, self.delay_value, dirs, heuristic, pause_wait)
        elif algorithm == "Bi BFS":
            result = bidirectional_bfs(self.grid, self.start_cell, self.end_cell, self.rectangles,
                                    self.canvas, stop_flag, self.delay_value, dirs, pause_wait)
        elif algorithm == "DFS":
            result = dfs(self.grid, self.start_cell, self.end_cell, self.rectangles,
                        self.canvas, stop_flag, self.delay_value, dirs, pause_wait)
        elif algorithm == "JPS":
            if self.move_mode.get() != "4":
                self.reset_button_colors()
                self.is_running = False
                try:
                    if hasattr(self, "move_toggle"):
                        self.move_toggle.configure(state="normal")
                    for algo in self.algorithm_buttons.values():
                        algo.configure(state="normal")
                except Exception:
                    pass
                messagebox.showinfo("Unsupported", "JPS supports 4-direction movement only.")
                return
            if not self.generated_maze:
                self.reset_button_colors()
                self.is_running = False
                try:
                    if hasattr(self, "move_toggle"):
                        self.move_toggle.configure(state="normal")
                    for algo in self.algorithm_buttons.values():
                        algo.configure(state="normal")
                except Exception:
                    pass
                messagebox.showinfo("Unsupported", "JPS works best with generated mazes. Please create a maze first.")
                return
            result = jps(self.grid, self.start_cell, self.end_cell, self.rectangles,
                        self.canvas, stop_flag, self.delay_value, pause_wait)

        end_time = perf_counter()
        self._pause_end()
        run_time = round((end_time - start_time) - self._pause_total, 2)

        if stop_flag():
            self.is_running = False
            try:
                if hasattr(self, "move_toggle"):
                    self.move_toggle.configure(state="normal")
                for algo in self.algorithm_buttons.values():
                    algo.configure(state="normal")
            except Exception:
                pass
            return

        if result:
            visited, path_length = result
            self.result_label.configure(text="Result: Path Found")
            self.visited_label.configure(text=f"Visited: {visited}")
            self.path_label.configure(text=f"Path length: {path_length}")
            self.time_label.configure(text=f"Run time: {run_time} seconds")
            if self.best_time is None or run_time < self.best_time:
                self.best_time = run_time
                self.fastest_algo = algorithm
                self.best_label.configure(text=f"Best: {self.fastest_algo} ({self.best_time} seconds)")
        elif not stop_flag():
            self.result_label.configure(text="Result: Path Not Found")
            self.visited_label.configure(text="Visited: 0")
            self.path_label.configure(text="Path length: 0")
            self.time_label.configure(text="Run time: 0 seconds")

        self.is_running = False
        try:
            if hasattr(self, "move_toggle"):
                self.move_toggle.configure(state="normal")
            for algo in self.algorithm_buttons.values():
                algo.configure(state="normal")
        except Exception:
            pass

    def reset_algorithm_visuals(self):
        self.stop_requested = True
        self.reset_button_colors()

        self.paused = False
        for item_id in getattr(self, "overlay_drawings", []):
            self.canvas.delete(item_id)
        for algo in self.algorithm_buttons.values():
                    algo.configure(state="normal")    
        self.overlay_drawings = []
        self._overlay_prev = None
        self.canvas.bind("<ButtonPress-1>", self.on_left_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        
        try:
            self._pause_end()
        except Exception:
            pass
        self._pause_total = 0.0
        self._pause_started_at = None
        if hasattr(self, "pause_btn"):
            self.pause_btn.configure(text="Pause Run (space)")
        self.paused = False
        # Clear search/path/time, keep Best
        reset_canvas_colors(GRID_ROWS, GRID_COLS, self.rectangles, self.canvas, self.start_cell, self.end_cell)
        self._clear_stats(clear_best=False)
        
    def _clear_stats(self, clear_best=False):
        if self.visited_label:
            self.visited_label.configure(text="Visited: 0")
        if self.path_label:
            self.path_label.configure(text="Path length: 0")
        if self.time_label:
            self.time_label.configure(text="Run time: 0 seconds")
        if self.result_label:
            self.result_label.configure(text="Result: N/A")
        if clear_best:
            self.best_time = None
            self.fastest_algo = None
            if self.best_label:
                self.best_label.configure(text="Best: N/A")

    def reset_all(self, reset_start=True):
        self.reset_button_colors()

        start = self.start_cell
        end = self.end_cell
        self.generated_maze = False
        self.stop_requested = True
        self.was_run = False
        self.is_running = False

        self.paused = False
        for item_id in getattr(self, "overlay_drawings", []):
            self.canvas.delete(item_id)
        for algo in self.algorithm_buttons.values():
                    algo.configure(state="normal")
        self.overlay_drawings = []
        self._overlay_prev = None
        self.canvas.bind("<ButtonPress-1>", self.on_left_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        
        try:
            self._pause_end()
        except Exception:
            pass
        self._pause_total = 0.0
        self._pause_started_at = None
        if hasattr(self, "pause_btn"):
            self.pause_btn.configure(text="Pause Run (space)")
        self.paused = False


        self._clear_stats(clear_best=True)

        self.start_cell = None
        self.end_cell = None

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                self.grid[row][col] = 0
                self.canvas.itemconfig(self.rectangles[row][col], fill=BACKGROUND_COLOR)
        if not reset_start:
            self.start_cell = start
            self.end_cell = end
        self.canvas.update()

    def generate_maze_recursive_backtracker(self, braid=0.18, avoid_2x2=True, avoid_stranded=True):
    # preserve existing points (even if reset clears them)
        prev_start = self.start_cell
        prev_end = self.end_cell
        had_start = prev_start is not None
        had_end = prev_end is not None

        self.reset_all(reset_start=False)

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                self.grid[row][col] = 1
                self.canvas.itemconfig(self.rectangles[row][col], fill=WALL_COLOR)

        visited = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        def is_valid(cell):
            r, c = cell
            return (0 <= r < GRID_ROWS) and (0 <= c < GRID_COLS) and (r % 2 == 1 and c % 2 == 1)

        def carve_passage_from(r, c):
            directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            random.shuffle(directions)
            visited[r][c] = True
            self.grid[r][c] = 0
            self.canvas.itemconfig(self.rectangles[r][c], fill=BACKGROUND_COLOR)

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                between_r, between_c = r + dr // 2, c + dc // 2
                if is_valid((nr, nc)) and not visited[nr][nc]:
                    self.grid[between_r][between_c] = 0
                    self.canvas.itemconfig(self.rectangles[between_r][between_c], fill=BACKGROUND_COLOR)
                    carve_passage_from(nr, nc)

        start_r = random.randrange(1, GRID_ROWS, 2)
        start_c = random.randrange(1, GRID_COLS, 2)
        carve_passage_from(start_r, start_c)
        #self.canvas.update()

        # ----- braiding helpers -----
        def wall_degree(r, c):
            deg = 0
            for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and self.grid[nr][nc] == 1:
                    deg += 1
            return deg

        def is_between_two_open_cells(r, c):
            if self.grid[r][c] != 1:
                return False
            if (r % 2 == 0) and (c % 2 == 1):
                if 0 < r < GRID_ROWS - 1:
                    return self.grid[r - 1][c] == 0 and self.grid[r + 1][c] == 0
            if (r % 2 == 1) and (c % 2 == 0):
                if 0 < c < GRID_COLS - 1:
                    return self.grid[r][c - 1] == 0 and self.grid[r][c + 1] == 0
            return False

        def would_create_2x2_open(r, c):
            rows, cols = GRID_ROWS, GRID_COLS
            candidates = [(r - 1, c - 1), (r - 1, c), (r, c - 1), (r, c)]
            for i, j in candidates:
                if 0 <= i < rows - 1 and 0 <= j < cols - 1:
                    cells = [(i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1)]
                    open_count = 0
                    for rr, cc in cells:
                        if (rr, cc) == (r, c):
                            continue
                        if self.grid[rr][cc] == 0:
                            open_count += 1
                    if open_count == 3:
                        return True
            return False

        def would_create_stranded_wall(r, c):
            if self.grid[r][c] != 1:
                return False
            for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and self.grid[nr][nc] == 1:
                    if wall_degree(nr, nc) <= 1:
                        return True
            return False

        if braid > 0.0:
            for r in range(1, GRID_ROWS - 1):
                for c in range(1, GRID_COLS - 1):
                    if is_between_two_open_cells(r, c) and random.random() < braid:
                        if avoid_2x2 and would_create_2x2_open(r, c):
                            continue
                        if avoid_stranded and would_create_stranded_wall(r, c):
                            continue
                        self.grid[r][c] = 0
                        self.canvas.itemconfig(self.rectangles[r][c], fill=BACKGROUND_COLOR)
            self.canvas.update()

        # ----- attach helper: ensure a given cell is open and connected to a corridor -----
        def open_and_attach(cell):
            r, c = cell
            # open this cell if it's a wall
            if self.grid[r][c] == 1:
                self.grid[r][c] = 0
                self.canvas.itemconfig(self.rectangles[r][c], fill=BACKGROUND_COLOR)

            # if all 4-neighbors are walls, open one neighbor (prefer odd/odd corridor direction)
            neighbors = [(-1,0),(1,0),(0,-1),(0,1)]
            has_open_neighbor = any(
                0 <= r+dr < GRID_ROWS and 0 <= c+dc < GRID_COLS and self.grid[r+dr][c+dc] == 0
                for dr, dc in neighbors
            )
            if not has_open_neighbor:
                # choose a neighbor that moves toward odd indices when possible
                candidates = []
                for dr, dc in neighbors:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                        score = 0
                        if nr % 2 == 1: score += 1
                        if nc % 2 == 1: score += 1
                        candidates.append((score, nr, nc))
                if candidates:
                    candidates.sort(reverse=True)
                    _, nr, nc = candidates[0]
                    self.grid[nr][nc] = 0
                    self.canvas.itemconfig(self.rectangles[nr][nc], fill=BACKGROUND_COLOR)

        # ----- place start/end depending on what exists -----
        open_cells = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if self.grid[r][c] == 0]

        if had_start and had_end:
            # keep existing locations
            self.start_cell = prev_start
            self.end_cell = prev_end
            open_and_attach(self.start_cell)
            open_and_attach(self.end_cell)

        elif had_start and not had_end:
            self.start_cell = prev_start
            open_and_attach(self.start_cell)
            choices = [cell for cell in open_cells if cell != self.start_cell]
            if not choices:
                messagebox.showerror("Error", "No empty cell available for end.")
                return
            self.end_cell = random.choice(choices)

        elif had_end and not had_start:
            self.end_cell = prev_end
            open_and_attach(self.end_cell)
            choices = [cell for cell in open_cells if cell != self.end_cell]
            if not choices:
                messagebox.showerror("Error", "No empty cell available for start.")
                return
            self.start_cell = random.choice(choices)

        else:
            # none existed: pick both
            if len(open_cells) < 2:
                messagebox.showerror("Error", "No empty cells for start and end.")
                return
            self.start_cell = random.choice(open_cells)
            self.end_cell = random.choice([cell for cell in open_cells if cell != self.start_cell])

        # if by any chance both equal, re-pick end
        if self.start_cell == self.end_cell:
            fallback = [cell for cell in open_cells if cell != self.start_cell]
            if fallback:
                self.end_cell = random.choice(fallback)

        # color start/end
        sr, sc = self.start_cell
        er, ec = self.end_cell
        self.canvas.itemconfig(self.rectangles[sr][sc], fill=START_COLOR)
        self.canvas.itemconfig(self.rectangles[er][ec], fill=END_COLOR)

        self.canvas.update()
        self.generated_maze = True

    def compare_all(self):
        # guard: cannot compare if something is running or paused
        if self.is_running or self.paused:
            messagebox.showinfo("Info", "Cannot compare while an algorithm is running or paused.")
            return
        if self.start_cell is None or self.end_cell is None:
            messagebox.showwarning("Error", "Start or end cell not set.")
            return

        # lock UI
        try:
            if hasattr(self, "move_toggle"):
                self.move_toggle.configure(state="disabled")
            for algo in self.algorithm_buttons.values():
                algo.configure(state="disabled")
            if hasattr(self, "pause_btn"):
                self.pause_btn.configure(state="disabled")
        except Exception:
            pass

        # reset "best" just for this comparison
        self.best_time = None
        self.fastest_algo = None
        if self.best_label:
            self.best_label.configure(text="Best: N/A")
        if self.result_label:
            self.result_label.configure(text="Result: Comparing all...")

        # which algorithms to run
        algos = ["BFS", "Bi BFS", "DFS", "A*"]
        # include JPS only when valid (4-dir and generated maze)
        if self.move_mode.get() == "4" and self.generated_maze:
            algos.append("JPS")

        # run each algorithm
        prev_delay = self.delay_value.get()
        self.delay_value.set(min(prev_delay, 0))  # for faster visualization

        for key in algos:
            self.run_search(key)
            if self.stop_requested:
                break  # in case a stop was triggered mid-way

        self.delay_value.set(prev_delay)

        # summary UI
        if self.fastest_algo:
            self.highlight_button(self.fastest_algo)
            if self.result_label:
                self.result_label.configure(text=f"Result: Best is {self.fastest_algo}")
        else:
            if self.result_label:
                self.result_label.configure(text="Result: Comparison finished")

        # unlock UI
        try:
            if hasattr(self, "move_toggle"):
                self.move_toggle.configure(state="normal")
            for algo in self.algorithm_buttons.values():
                algo.configure(state="normal")
            if hasattr(self, "pause_btn"):
                self.pause_btn.configure(state="normal")
        except Exception:
            pass


def show_gui():
    root = ttk.Window(themename="morph")
    root.title("Maze Visualizer")
    my_font = ctk.CTkFont(family="Arial", size=15, weight="bold", slant="italic")
    header_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="italic")

    title_label = ttk.Label(root, text="Maze Solving Algorithms Visualizer", font=header_font)
    title_label.pack(pady=(10, 5))

    main_frame = ttk.Frame(root, borderwidth="10")
    main_frame.pack()
    algorithm_buttons = {}

    # ===== Left sidebar: Legend + Stats =====
    left_sidebar = ttk.Frame(main_frame)
    left_sidebar.pack(side=tk.LEFT, padx=(10), pady=10, fill=tk.Y)

    # ===== Stats =====
    stats_frame = ttk.LabelFrame(left_sidebar, border="10", text="Stats")
    stats_frame.pack(fill=tk.X)
    result_label = ctk.CTkLabel(stats_frame, text="Result: N/A", text_color="#7A7A7A", font=my_font)
    result_label.pack(anchor="w", pady=3)
    visited_label = ctk.CTkLabel(stats_frame, text="Visited: 0", text_color="#7A7A7A", font=my_font)
    visited_label.pack(padx=(0, 5), anchor = "w")
    path_label = ctk.CTkLabel(stats_frame, text="Path length: 0", text_color="#7A7A7A", font=my_font)
    path_label.pack(padx=(0, 5), anchor = "w")
    time_label = ctk.CTkLabel(stats_frame, text="Run time: 0 seconds", text_color="#7A7A7A", font=my_font)
    time_label.pack(padx=(0, 5), anchor = "w")
    best_label = ctk.CTkLabel(stats_frame, text="Best: N/A", text_color="#7A7A7A", font=my_font)
    best_label.pack(padx=(0, 5), anchor = "w")


    # ===== Legend =====
    legend_frame = ttk.LabelFrame(left_sidebar, text="Legend", border="10")
    legend_frame.pack(fill=tk.X, pady=(10, 10))

    # two equal-width columns inside the legend
    legend_frame.grid_columnconfigure(0, weight=1, uniform="legend")
    legend_frame.grid_columnconfigure(1, weight=1, uniform="legend")

    col_left = ctk.CTkFrame(legend_frame, fg_color="transparent")
    col_left.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=6)

    col_right = ctk.CTkFrame(legend_frame, fg_color="transparent")
    col_right.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=6)

    def add_legend_color(parent, color, label_text, appearance=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)

        if appearance is None:
            appearance = ctk.get_appearance_mode()
        border = "#CFCFCF" if appearance == "Light" else "#1F2937"

        swatch = ctk.CTkFrame(
            row, width=18, height=18,
            fg_color=color, corner_radius=4,
            border_width=1, border_color=border
        )
        swatch.pack(side="left", padx=(2, 8), pady=2)
        swatch.pack_propagate(False)

        label = ctk.CTkLabel(row, text=label_text, text_color="#7A7A7A", font=my_font, anchor="w")
        label.pack(side="left")

    # left column: Start / End / Wall
    add_legend_color(col_left, START_COLOR, "Start")
    add_legend_color(col_left, END_COLOR, "End")
    add_legend_color(col_left, WALL_COLOR, "Wall")

    # right column: Path / Search
    add_legend_color(col_right, PATH_COLOR, "Final Path")
    add_legend_color(col_right, SEARCH_COLOR, "Search Path")

    # ===== How to instructions =====
    howto_frame = ttk.LabelFrame(left_sidebar, border="10", text="How to use")
    howto_frame.pack(fill=tk.X)
    how_to_text = """
    1. Right-click to set start (green) 
        and end (red) points
    2. Left-click to draw/erase walls
    3. Use 'Create Maze' to generate a 
        random maze
    4. Select an algorithm to run
    5. Use 'Compare All' to run all 
        algorithms and find the fastest
    6. Adjust the delay slider to control 
        visualization speed
    7. Click Pause to pause the run and 
        enable on screen drawing
    8. Reset Run to clear visualization
    9. Reset All to clear everything  
    10. Keyboard Shortcuts in brackets
    """
    howto_label = ctk.CTkLabel(howto_frame, text=how_to_text, text_color="#7A7A7A", anchor="w", justify="left",
                               font=my_font)
    howto_label.pack(fill="x")


    # ===== Canvas in the center =====
    canvas_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ===== Control panel on the right =====
    control_frame = tk.Frame(main_frame, padx=10, pady=10, bg=BACKGROUND_COLOR)
    control_frame.pack(side=tk.LEFT, fill=tk.Y)

    ctk.CTkButton(
        control_frame,
        text="Create Maze (m)",
        font=my_font,
        fg_color="#32993F",
        hover_color="#44C956",
        width=180,
        height=32,
        corner_radius=10,
        border_color="black",
        border_width=2,
        command=lambda: gui.generate_maze_recursive_backtracker(),
    ).pack(pady=(30, 10))

    ttk.Label(control_frame, text="Search Algorithms", font=header_font).pack(pady=(20, 10))

    algorithm_descriptions = {
        "BFS": "Breadth-First Search: Explores all neighbors at the current depth before going deeper. Guarantees shortest path.",
        "Bi BFS": "Bidirectional BFS: Runs two simultaneous BFS searches — one from start, one from end — and stops when they meet. Faster in many cases.",
        "DFS": "Depth-First Search: Explores as far as possible along each branch before backtracking. Not guaranteed to find the shortest path.",
        "A*": "A* Search: Uses heuristics to guide the search. Guarantees shortest path and is usually fast.",
        "JPS": "Jump Point Search: Optimized for uniform-cost grids. Skips unnecessary nodes and accelerates A* search. Best with open mazes.",
    }

    def create_algo_button(name, algo_key):
        row = ttk.Frame(control_frame)
        row.pack(pady=5, anchor="w")

        btn = ctk.CTkButton(
            row,
            text=name,
            font=my_font,
            border_color="black",
            border_width=2,
            width=200,
            hover_color="#144870",
            command=lambda: gui.run_search(algo_key),
        )
        btn.pack(side=ctk.LEFT, padx=(0, 10))

        info_btn = ctk.CTkButton(
            row,
            text="ℹ",
            fg_color="#33B6B6",
            width=40,
            hover_color="#1AE7E7",
            command=lambda: show_info(algo_key),
        )
        info_btn.pack(padx=(10, 0))

        algorithm_buttons[algo_key] = btn

    def show_info(algo_key):
        desc = algorithm_descriptions.get(algo_key, "No description available.")
        messagebox.showinfo("info", desc)

    create_algo_button("Run BFS (1)", "BFS")
    create_algo_button("Run Bidirectional BFS (2)", "Bi BFS")
    create_algo_button("Run DFS (3)", "DFS")
    create_algo_button("Run A* (4)", "A*")
    create_algo_button("Run JumpPoint Search (5)", "JPS")

    ctk.CTkButton(
        control_frame,
        text="Compare All Algorithms (c)",
        font=my_font,
        width=250,
        border_color="black",
        border_width=2,
        fg_color="#6C5DD3",
        hover_color="#8F84F7",
        command=lambda: gui.compare_all(),
    ).pack(pady=(20, 10))


    gui = MazeGUI(canvas_frame, visited_label, path_label, time_label, best_label, algorithm_buttons=algorithm_buttons, result_label=result_label)

    ttk.Label(control_frame, text="Movement", font=header_font).pack(pady=(10, 6))
    move_toggle = ctk.CTkSegmentedButton(
        control_frame,
        values=["4", "8"],
        variable=gui.move_mode
    )
    move_toggle.pack(pady=(0, 10))
    gui.move_toggle = move_toggle


    pause_btn = ctk.CTkButton(
        control_frame,
        text="Pause Run (space)",
        width=100,
        font=my_font,
        border_color="black",
        fg_color="#B44A4A",
        hover_color="#BD6D6D",
        corner_radius=20,
        border_width=2,
        command=lambda: gui.toggle_pause(),
    )
    pause_btn.pack(pady=(30, 10))
    gui.pause_btn = pause_btn

    ttk.Label(control_frame, text="Algorithm delay (ms)", font=header_font).pack(pady=(30, 10))

    ctk.CTkButton(
        control_frame,
        text="Full Reset (ctrl+r)",
        width=200,
        font=my_font,
        border_color="black",
        border_width=2,
        command=lambda: gui.reset_all(),
    ).pack(side=tk.BOTTOM, pady=(5, 5))

    ctk.CTkButton(
        control_frame,
        text="Reset Run (r)",
        font=my_font,
        width=200,
        border_color="black",
        border_width=2,
        command=lambda: gui.reset_algorithm_visuals(),
    ).pack(side=tk.BOTTOM, pady=(50, 5))

    delay_value_label = ttk.Label(control_frame, text=f"Delay: {gui.delay_value.get():.0f} ms", font=my_font)
    delay_value_label.pack()

    def update_delay_label(val):
        delay_value_label.config(text=f"Delay: {int(float(val))} ms")

    delay_slider = ctk.CTkSlider(
        control_frame,
        from_=0,
        to=30,
        number_of_steps= 10,
        variable=gui.delay_value,
        progress_color="blue",
        command=update_delay_label,
    )
    delay_slider.pack(pady=10)

    def on_close():
        try:
            gui.stop_requested = True
            gui.paused = False
            if hasattr(gui, "_pause_end"):
                try:
                    gui._pause_end()
                except Exception:
                    pass
            try:
                gui.canvas.update()
            except Exception:
                pass
        finally:
            try:
                root.destroy()
            except Exception:
                pass

    root.protocol("WM_DELETE_WINDOW", on_close)

    # --- keyboard shortcuts (press-only, swallow events) ---
    def bind_shortcuts(root, gui):
        def call_async(fn):
            def _h(e):
                root.after(0, fn)  # avoid blocking UI
                return "break"
            return _h

        def call_async_if_running(fn):
            def _h(e):
                if gui.is_running or gui.paused:
                    root.after(0, fn)
                return "break"
            return _h

        def run_algo(algo_key):
            # allow switch only if not running or if paused
            if gui.is_running and not gui.paused:
                return
            gui.run_search(algo_key)

        root.bind_all("<KeyPress-m>", call_async(gui.generate_maze_recursive_backtracker))
        # Space: pause/resume only if a run exists or paused
        root.bind_all("<KeyPress-space>", call_async_if_running(gui.toggle_pause))

        # R: Reset Run
        root.bind_all("<KeyPress-r>", call_async(gui.reset_algorithm_visuals))
        # Ctrl+R: Full Reset
        root.bind_all("<Control-KeyPress-r>", call_async(gui.reset_all))

        # 1..5: run algos
        root.bind_all("<KeyPress-1>", lambda e: (root.after(0, lambda: run_algo("BFS")), "break")[1])
        root.bind_all("<KeyPress-2>", lambda e: (root.after(0, lambda: run_algo("Bi BFS")), "break")[1])
        root.bind_all("<KeyPress-3>", lambda e: (root.after(0, lambda: run_algo("DFS")), "break")[1])
        root.bind_all("<KeyPress-4>", lambda e: (root.after(0, lambda: run_algo("A*")), "break")[1])
        root.bind_all("<KeyPress-5>", lambda e: (root.after(0, lambda: run_algo("JPS")), "break")[1])

        # C: Compare All 
        root.bind_all("<KeyPress-c>", lambda e: (root.after(0, gui.compare_all) if not (gui.is_running or gui.paused) else None, "break")[1])

    bind_shortcuts(root, gui)


    return gui, root
