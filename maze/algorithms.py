from heapq import heappush, heappop
from collections import deque

from maze.utils import manhattan_distance, delay_step, is_in_bounds

SEARCH_COLOR2 = "#FFB74A"
SEARCH_COLOR = "#26BEFA"
PATH_COLOR = "#E3FC00"


def _maybe_pause(pause_wait):
    if pause_wait:
        pause_wait()

def bfs(grid, start, end, canvas_rectangles, canvas, stop_flag, delay_value, dirs, pause_wait=None):
    rows, cols = len(grid), len(grid[0])
    queue = deque([start])
    visited = set([start])
    parents = {}

    while queue:
        if stop_flag():
            return False

        _maybe_pause(pause_wait)
        if stop_flag():
            return False

        r, c = queue.popleft()
        if (r, c) == end:
            path_length = reconstruct_path(
                parents, start, end, canvas_rectangles, canvas, delay_value, stop_flag, pause_wait
            )
            return len(visited), path_length

        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if is_in_bounds(nr, nc, rows, cols):
                if grid[nr][nc] == 0 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
                    parents[(nr, nc)] = (r, c)

                    if (nr, nc) != end:
                        canvas.itemconfig(canvas_rectangles[nr][nc], fill=SEARCH_COLOR)
                        delay_step(canvas, delay_value)
                        _maybe_pause(pause_wait)
                    if stop_flag():
                        return False

    return False

def a_star(grid, start, end, canvas_rectangles, canvas, stop_flag, delay_value, dirs, heuristic=manhattan_distance, pause_wait=None):
    rows, cols = len(grid), len(grid[0])
    open_set = []
    heappush(open_set, (heuristic(start, end), 0, start))

    parents = {}
    g_score = {start: 0}
    visited = set()

    while open_set:
        if stop_flag():
            return False

        _maybe_pause(pause_wait)
        if stop_flag():
            return False

        _, current_g, current = heappop(open_set)
        if current == end:
            path_length = reconstruct_path(
                parents, start, end, canvas_rectangles, canvas, delay_value, stop_flag, pause_wait
            )
            return len(visited), path_length

        if current in visited:
            continue
        visited.add(current)

        r, c = current
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)

            if is_in_bounds(nr, nc, rows, cols) and grid[nr][nc] == 0:
                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, end)
                    heappush(open_set, (f_score, tentative_g, neighbor))
                    parents[neighbor] = current

                    if neighbor != end:
                        canvas.itemconfig(canvas_rectangles[nr][nc], fill=SEARCH_COLOR)
                        if stop_flag():
                            return False
                        delay_step(canvas, delay_value)
                        _maybe_pause(pause_wait)
                        if stop_flag():
                            return False

    return False

def bidirectional_bfs(grid, start, end, canvas_rectangles, canvas, stop_flag, delay_value, dirs, pause_wait=None):
    rows, cols = len(grid), len(grid[0])

    if start == end:
        return True

    queue_start = deque([start])
    queue_end = deque([end])

    visited_start = {start}
    visited_end = {end}

    parents_start = {}
    parents_end = {}

    meeting_point = None

    while queue_start and queue_end:
        if stop_flag():
            return False

        _maybe_pause(pause_wait)
        if stop_flag():
            return False

        if queue_start:
            curr = queue_start.popleft()
            if curr in visited_end:
                meeting_point = curr
                break

            for dr, dc in dirs:
                nr, nc = curr[0] + dr, curr[1] + dc
                nb = (nr, nc)
                if is_in_bounds(nr, nc, rows, cols) and grid[nr][nc] == 0 and nb not in visited_start:
                    visited_start.add(nb)
                    queue_start.append(nb)
                    parents_start[nb] = curr

                    if nb != end and nb != start:
                        canvas.itemconfig(canvas_rectangles[nr][nc], fill=SEARCH_COLOR)
                        if stop_flag():
                            return False
                        delay_step(canvas, delay_value)
                        _maybe_pause(pause_wait)
                        if stop_flag():
                            return False

        if queue_end:
            curr = queue_end.popleft()
            if curr in visited_start:
                meeting_point = curr
                break

            for dr, dc in dirs:
                nr, nc = curr[0] + dr, curr[1] + dc
                nb = (nr, nc)
                if is_in_bounds(nr, nc, rows, cols) and grid[nr][nc] == 0 and nb not in visited_end:
                    visited_end.add(nb)
                    queue_end.append(nb)
                    parents_end[nb] = curr

                    if nb != end and nb != start:
                        canvas.itemconfig(canvas_rectangles[nr][nc], fill=SEARCH_COLOR2)
                        if stop_flag():
                            return False
                        delay_step(canvas, delay_value)
                        _maybe_pause(pause_wait)
                        if stop_flag():
                            return False

    if meeting_point:
        path_length = reconstruct_bidirectional_path(
            parents_start, parents_end, start, end, meeting_point,
            canvas_rectangles, canvas, delay_value, stop_flag, pause_wait
        )
        return len(parents_start) + len(parents_end) + 1, path_length

    else:
        return False

def dfs(grid, start, end, canvas_rectangles, canvas, stop_flag, delay_value, dirs, pause_wait=None):
    rows, cols = len(grid), len(grid[0])
    stack = [start]
    visited = set([start])
    parents = {}

    while stack:
        if stop_flag():
            return False

        _maybe_pause(pause_wait)
        if stop_flag():
            return False

        current = stack.pop()
        if current == end:
            path_length = reconstruct_path(
                parents, start, end, canvas_rectangles, canvas, delay_value, stop_flag, pause_wait
            )
            return len(visited), path_length

        r, c = current

        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)

            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and neighbor not in visited:
                parents[neighbor] = current

                # early exit on discovery of the goal
                if neighbor == end:
                    path_length = reconstruct_path(
                        parents, start, end, canvas_rectangles, canvas, delay_value, stop_flag, pause_wait
                    )
                    # +1 to count the end as visited (optional)
                    return len(visited) + 1, path_length

                visited.add(neighbor)
                stack.append(neighbor)

                if neighbor != start and neighbor != end:
                    canvas.itemconfig(canvas_rectangles[nr][nc], fill=SEARCH_COLOR)
                    delay_step(canvas, delay_value)
                    if stop_flag():
                        return False
                    _maybe_pause(pause_wait)

    return False

def jps(grid, start, end, canvas_rectangles, canvas, stop_flag, delay_value, pause_wait=None):
    rows, cols = len(grid), len(grid[0])
    visited = set()
    open_set = []
    g_cost = {start: 0}
    parents = {}

    def jump(r, c, dr, dc):
        while True:
            r += dr
            c += dc
            if not is_in_bounds(r, c, rows, cols) or grid[r][c] != 0:
                return None
            if (r, c) == end:
                return (r, c)

            if dr != 0:
                if (is_in_bounds(r, c + 1, rows, cols) and grid[r][c + 1] == 0 and
                    is_in_bounds(r - dr, c + 1, rows, cols) and grid[r - dr][c + 1] == 1):
                    return (r, c)
                if (is_in_bounds(r, c - 1, rows, cols) and grid[r][c - 1] == 0 and
                    is_in_bounds(r - dr, c - 1, rows, cols) and grid[r - dr][c - 1] == 1):
                    return (r, c)

            elif dc != 0:
                if (is_in_bounds(r + 1, c, rows, cols) and grid[r + 1][c] == 0 and
                    is_in_bounds(r + 1, c - dc, rows, cols) and grid[r + 1][c - dc] == 1):
                    return (r, c)
                if (is_in_bounds(r - 1, c, rows, cols) and grid[r - 1][c] == 0 and
                    is_in_bounds(r - 1, c - dc, rows, cols) and grid[r - 1][c - dc] == 1):
                    return (r, c)

    def add_jump_neighbors(r, c):
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            jp = jump(r, c, dr, dc)
            if jp and jp not in visited:
                nr, nc = jp
                new_cost = g_cost[(r, c)] + manhattan_distance((r, c), (nr, nc))
                if jp not in g_cost or new_cost < g_cost[jp]:
                    g_cost[jp] = new_cost
                    f = new_cost + manhattan_distance(jp, end)
                    heappush(open_set, (f, jp))
                    parents[jp] = (r, c)

    heappush(open_set, (manhattan_distance(start, end), start))
    g_cost[start] = 0

    while open_set:
        if stop_flag():
            return False

        _maybe_pause(pause_wait)
        if stop_flag():
            return False

        _, (r, c) = heappop(open_set)

        if (r, c) in visited:
            continue
        visited.add((r, c))

        if (r, c) != start and (r, c) != end:
            canvas.itemconfig(canvas_rectangles[r][c], fill=SEARCH_COLOR)
            delay_step(canvas, delay_value)
            _maybe_pause(pause_wait)
            if stop_flag():
                return False

        if (r, c) == end:
            path_length = reconstruct_path(
                parents, start, end, canvas_rectangles, canvas, delay_value, stop_flag, pause_wait
            )
            return len(visited), path_length

        add_jump_neighbors(r, c)

    return False

def reconstruct_path(parents, start, end, canvas_rectangles, canvas, delay_value, stop_flag, pause_wait=None):
    def line_between(a, b):
        r1, c1 = a
        r2, c2 = b
        dr = (r2 - r1)
        dc = (c2 - c1)
        if dr:
            dr //= abs(dr)
        if dc:
            dc //= abs(dc)
        cells = []
        r, c = r1 + dr, c1 + dc
        while (r, c) != b:
            cells.append((r, c))
            r += dr
            c += dc
        return cells

    curr = end
    path_cells = []
    while curr in parents:
        prev = parents[curr]
        if abs(curr[0] - prev[0]) + abs(curr[1] - prev[1]) > 1:
            path_cells.extend(line_between(prev, curr))
        path_cells.append(curr)
        curr = prev

    for cell in reversed(path_cells):
        if stop_flag():
            return False
        _maybe_pause(pause_wait)

        if cell != start and cell != end:
            r, c = cell
            rect = canvas_rectangles[r][c]
            canvas.itemconfig(rect, fill=PATH_COLOR)
            delay_step(canvas, delay_value)
            _maybe_pause(pause_wait)

    return len(path_cells)

def reconstruct_bidirectional_path(
    parents_start, parents_end, start, end, meeting_point,
    canvas_rectangles, canvas, delay_value, stop_flag, pause_wait=None
):
    path = []
    curr = meeting_point
    while curr != start:
        path.append(curr)
        curr = parents_start[curr]
    path.append(start)
    path.reverse()
    curr = parents_end.get(meeting_point)
    while curr and curr != end:
        path.append(curr)
        curr = parents_end[curr]
    if curr == end:
        path.append(end)

    path_length = 0
    for cell in path:
        if stop_flag():
            return False
        _maybe_pause(pause_wait)

        if cell != start and cell != end:
            r, c = cell
            rect = canvas_rectangles[r][c]
            canvas.itemconfig(rect, fill=PATH_COLOR)
            path_length += 1
            delay_step(canvas, delay_value)
            _maybe_pause(pause_wait)

    return path_length + 1
