# Life Cell Simulator

The Life Cell Simulator is a Python implementation of Conway's Game of Life, supporting both graphical (Pygame) and text-based (CLI) modes. The program can dynamically switch between modes or fall back to the text-only version if the graphical mode cannot be started.

---

## Features

### General
- Implements Conway's Game of Life rules
- Supports graphical (GUI) mode using Pygame for a visual experience
- Includes text-only (CLI) mode for environments where graphical mode is unavailable
- Falls back to CLI mode automatically if GUI mode fails, with a user notification
- Interactive controls in both modes
- Random initial grid generation by default

### Graphical Mode (GUI)
- Displays live and dead cells as colored squares in a window
- Adjustable grid size and cell size via arguments
- Interactive controls:
  - `SPACE`: Pause/unpause simulation
  - `R`: Reset grid with random live cells
  - `C`: Clear the grid (all cells dead)
  - `UP/DOWN ARROWS`: Adjust simulation speed
  - Close the window or press `ESC` to exit

### Text-Only Mode (CLI)
- Renders the grid using ASCII characters:
  - `#` for live cells
  - `.` for dead cells
- Dynamically updates the grid in the terminal
- Interactive controls:
  - `SPACE`: Pause/unpause simulation
  - `ENTER`: Add a new live cell at a random location
  - `Ctrl+C`: Exit the simulation
- Status display showing current simulation state

---

## Requirements

- Python 3.6 or higher
- Pygame (for GUI mode)

To install Pygame, run:
```bash
pip install pygame
```

## Running the Simulator

Save the script as `life_simulator.py` and run it from the terminal using one of the following modes.

### Graphical Mode (GUI)
```bash
python life_simulator.py --gui
```

### Text-Only Mode (CLI)
```bash
python life_simulator.py --text
```

## Mode Selection

The program implements automatic mode selection. When no specific mode is indicated, it attempts to launch in GUI mode first. If GUI mode initialization fails due to missing dependencies, the system automatically switches to text-only mode.

## Command-Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--rows` | 20 | Number of rows in the grid |
| `--cols` | 30 | Number of columns in the grid |
| `--cell_size` | 20 | Size of each cell in pixels (GUI mode only) |
| `--speed` | 0.5 | Update interval in seconds (CLI mode only) |
| `--gui` | None | Force graphical mode |
| `--text` | None | Force text-only mode |

## Example Commands

### Graphical Mode with Custom Grid
```bash
python life_simulator.py --gui --rows 25 --cols 40 --cell_size 15
```

### Text-Only Mode with Custom Speed
```bash
python life_simulator.py --text --rows 30 --cols 50 --speed 0.3
```

### Automatic Mode Selection
```bash
python life_simulator.py
```

## Code Structure

The simulator is built around several core functions that handle different aspects of the simulation:

* `create_grid(rows, cols)`: Initializes the grid with random live or dead cells
* `count_neighbors(grid, x, y)`: Counts live neighbors around a given cell
* `next_generation(grid)`: Computes the next state of the grid based on Conway's rules
* `run_text_mode(rows, cols, speed)`: Runs the text-based version of the simulator
* `run_gui_mode(rows, cols, cell_size, speed)`: Runs the graphical version of the simulator
* `main()`: Handles argument parsing, mode selection, and fallback logic

## Future Enhancements

The following features are planned for future development:

* Support for saving and loading grid states
* Introduction of preset patterns (e.g., gliders, oscillators)
* Interactive cell toggling in GUI mode
* Extended CLI mode with customizable symbols for live/dead cells

## License

This project is licensed under the MIT License. Users are free to use, modify, and distribute the code.

For more information, please visit the original repository at: Life Cell Simulator Repository
For any questions or concerns, please contact istvan@airobotika.com.