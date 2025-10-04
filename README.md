# 🔍 Search Algorithms Visualizer

An interactive Python-based visualizer for popular pathfinding algorithms using a maze/grid environment. Built with `ttkbootstrap`, this project lets users visualize how different search algorithms traverse a maze, offering both real-time feedback and performance statistics.

## Features

- **Algorithms Supported**:
  - **BFS (Breadth-First Search)**
  - **DFS (Depth-First Search)**
  - **A*** **(A Star Search)**
  - **Bidirectional BFS**
  - **Jump Point Search (JPS)**

- **Interactive Maze Creation**:
  - **Draw walls manually** with left-click or drag.
  - **Place start and End points** witn right-click.
  - **Remove an existing wall** with an additional left-click.
  - **Reset Start and End points** with another right-click cycle.

- **Maze Generator**:
  - Generate a **random maze** using the **Recursive Backtracker algorithm**.

- **Algorithm Controls**:
  - Info button (`ℹ️`) for each algorithm shows a short description.
  - Slider to **adjust algorithm speed (delay)**.
  - Two reset options:
    - **Reset Path**: Clears only the algorithm trace.
    - **Reset Maze**: Clears everything including walls and points.

- **Statistics Panel**:
  - Number of cells visited.
  - Final path length.
  - Time taken to solve.
  - Best time recorded for solving a maze.

- **Color Legend**:
  - Indicates start, end, walls, visited nodes, and final path.

## Preview
![alt text](Visualization.gif)

## Project Structure

- **Algorithms_Visualization/**:
  - maze/
    - gui.py ; Handles UI with ttkbootstrap and canvas drawing
    - algorithms.py ; Implements all pathfinding algorithms
    - utils.py ; Utility functions
    - init.py
  - main.py ; Entry point to launch the visualizer


## Technologies Used

- Python 3
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) (for modern UI styling)
- `tkinter` (for canvas and user interaction)
- Standard Python libraries: `random`, `collections`, `time`

##  Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/AfikHaviv/Algorithms_Visualization.git
cd Algorithms_Visualization
```

### 2. Install dependencies
```bash
pip install ttkbootstrap
```

### 3. Run the application
```bash
python main.py
```

## How to Use

1. **Set Start and End Points**: Right-click on empty cells to place start (green) and end (red) points
2. **Draw Walls**: Left-click and drag to create walls (black cells)
3. **Generate Random Maze**: Click the "Generate Maze" button for an automatic maze
4. **Select Algorithm**: Choose from BFS, DFS, A*, Bidirectional BFS, or Jump Point Search
5. **Adjust Speed**: Use the speed slider to control visualization speed
6. **Run Visualization**: Click "Start" to watch the algorithm in action
7. **View Statistics**: Check the stats panel for performance metrics

## Algorithm Information

- **BFS**: Guarantees shortest path, explores level by level
- **DFS**: Uses stack-based approach, may not find shortest path
- **A***: Uses heuristic function for optimal pathfinding
- **Bidirectional BFS**: Searches from both start and end simultaneously
- **Jump Point Search**: Optimized A* for grid-based pathfinding


