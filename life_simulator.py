"""
Life Cell Simulator - A Python implementation of Conway's Game of Life.

This module provides both graphical (Pygame) and text-based interfaces for simulating
cellular automata based on Conway's Game of Life rules. It supports interactive controls,
adjustable simulation speeds, and dynamic mode switching between GUI and CLI versions.
"""

import argparse
import os
import random
import select
import sys
import termios
import time
import tty
from typing import List, Optional

# Optional: Try to import msvcrt on Windows
if sys.platform == "win32":
    try:
        import msvcrt
    except ImportError:
        msvcrt = None
else:
    msvcrt = None

# Optional: Try to import Pygame. If unavailable, set a fallback flag.
try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Configuration constants
SIMULATION_CONFIG = {
    "min_speed": 1,
    "max_speed": 60,
    "speed_increment": 5,
    "default_fps": 10,
}

COLORS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "alive": (50, 205, 50),  # Green for alive cells
    "dead": (30, 30, 30),  # Dark gray for dead cells
}


def is_key_pressed() -> Optional[str]:
    """Check if a key was pressed without blocking.

    Returns:
        Optional[str]: The pressed key character if available, None otherwise.
    """
    if sys.platform != "win32":
        # Unix-like systems
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None

    # Windows systems
    if msvcrt:
        return msvcrt.getch().decode("utf-8") if msvcrt.kbhit() else None
    return None


class LifeSimulator:
    """Manages the core logic for Conway's Game of Life simulation."""

    def __init__(self, rows: int, cols: int):
        """Initialize the simulator with given dimensions.

        Args:
            rows (int): Number of rows in the grid
            cols (int): Number of columns in the grid
        """
        self.rows = rows
        self.cols = cols
        self.grid = self.create_grid(randomize=True)

    def create_grid(self, randomize: bool = False) -> List[List[int]]:
        """Initialize the grid with dead cells or random live cells.

        Args:
            randomize (bool): If True, randomly populate the grid with live cells

        Returns:
            List[List[int]]: The initialized grid
        """
        if randomize:
            return [
                [random.choice([0, 1]) for _ in range(self.cols)]
                for _ in range(self.rows)
            ]
        return [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def count_neighbors(self, x: int, y: int) -> int:
        """Count the live neighbors around a cell.

        Args:
            x (int): Row index of the cell
            y (int): Column index of the cell

        Returns:
            int: Number of live neighbors
        """
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        count = 0
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.rows and 0 <= ny < self.cols:
                count += self.grid[nx][ny]
        return count

    def next_generation(self) -> None:
        """Compute the next state of the grid based on Conway's rules."""
        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for x in range(self.rows):
            for y in range(self.cols):
                neighbors = self.count_neighbors(x, y)
                if self.grid[x][y] == 1:
                    # Survival: 2 or 3 neighbors
                    new_grid[x][y] = 1 if neighbors in (2, 3) else 0
                else:
                    # Birth: exactly 3 neighbors
                    new_grid[x][y] = 1 if neighbors == 3 else 0
        self.grid = new_grid


class TextInterface:
    """Handles the text-based interface for the Life simulator."""

    def __init__(self, simulator: LifeSimulator):
        """Initialize the text interface.

        Args:
            simulator (LifeSimulator): The life simulation instance
        """
        self.simulator = simulator
        self.update_rate = SIMULATION_CONFIG["default_fps"]
        self.running = True
        self.paused = False

    def display_grid(self) -> None:
        """Display the current grid state in text mode."""
        os.system("cls" if os.name == "nt" else "clear")
        for row in self.simulator.grid:
            print("".join("#" if cell else "." for cell in row))
        self.display_controls()

    def display_controls(self) -> None:
        """Display the control information."""
        print("\nControls:")
        print("Space: Pause/Resume")
        print("R: Reset grid with random cells")
        print("C: Clear grid")
        print("+/-: Adjust speed")
        print("ESC or Ctrl+C: Exit")
        print(f"\nStatus: {'Paused' if self.paused else 'Running'}")
        print(f"Speed: {self.update_rate} updates/second")

    def handle_input(self) -> None:
        """Handle user input for the text interface."""
        key = is_key_pressed()
        if not key:
            return

        if key == " ":
            self.paused = not self.paused
        elif key.lower() == "r":
            self.simulator.grid = self.simulator.create_grid(randomize=True)
        elif key.lower() == "c":
            self.simulator.grid = self.simulator.create_grid(randomize=False)
        elif key == "\x1b":  # ESC key
            self.running = False
        elif key in ("+", "="):
            self.update_rate = min(SIMULATION_CONFIG["max_speed"], self.update_rate + 1)
        elif key == "-":
            self.update_rate = max(SIMULATION_CONFIG["min_speed"], self.update_rate - 1)

    def run(self) -> None:
        """Run the text-based simulation loop."""
        if sys.platform != "win32":
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setcbreak(sys.stdin.fileno())
                self._run_simulation_loop()
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        else:
            self._run_simulation_loop()

    def _run_simulation_loop(self) -> None:
        """Internal simulation loop implementation."""
        try:
            while self.running:
                self.display_grid()
                self.handle_input()
                if not self.paused:
                    self.simulator.next_generation()
                time.sleep(1 / self.update_rate)
        except KeyboardInterrupt:
            print("\nSimulation ended.")


class GUISettings:
    """Stores GUI-specific settings and configuration."""

    def __init__(self, cell_size: int):
        """Initialize GUI settings.

        Args:
            cell_size (int): Size of each cell in pixels
        """
        self.cell_size = cell_size
        self.fps = SIMULATION_CONFIG["default_fps"]
        self.paused = False


class GUIInterface:
    """Handles the graphical interface for the Life simulator."""

    def __init__(self, simulator: LifeSimulator, cell_size: int):
        """Initialize the GUI interface.

        Args:
            simulator (LifeSimulator): The life simulation instance
            cell_size (int): Size of each cell in pixels
        """
        self.simulator = simulator
        self.settings = GUISettings(cell_size)
        self.width = simulator.cols * cell_size
        self.height = simulator.rows * cell_size
        self.running = True

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Conway's Game of Life")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

    def _handle_keydown(self, key: int) -> None:
        """Handle keyboard input events.

        Args:
            key (int): The pygame key constant
        """
        if key == pygame.K_SPACE:
            self.settings.paused = not self.settings.paused
        elif key == pygame.K_r:
            self.simulator.grid = self.simulator.create_grid(randomize=True)
        elif key == pygame.K_c:
            self.simulator.grid = self.simulator.create_grid(randomize=False)
        elif key in (pygame.K_UP, pygame.K_PLUS, pygame.K_KP_PLUS):
            self.settings.fps = min(
                SIMULATION_CONFIG["max_speed"],
                self.settings.fps + SIMULATION_CONFIG["speed_increment"],
            )
        elif key in (pygame.K_DOWN, pygame.K_MINUS, pygame.K_KP_MINUS):
            self.settings.fps = max(
                SIMULATION_CONFIG["min_speed"],
                self.settings.fps - SIMULATION_CONFIG["speed_increment"],
            )
        elif key == pygame.K_ESCAPE:
            self.running = False

    def draw(self) -> None:
        """Draw the current state of the grid."""
        self.screen.fill(COLORS["white"])

        for x in range(self.simulator.rows):
            for y in range(self.simulator.cols):
                color = COLORS["alive"] if self.simulator.grid[x][y] else COLORS["dead"]
                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        y * self.settings.cell_size,
                        x * self.settings.cell_size,
                        self.settings.cell_size,
                        self.settings.cell_size,
                    ),
                )

        # Display current speed
        speed_text = self.font.render(
            f"Speed: {self.settings.fps} FPS", True, COLORS["black"]
        )
        self.screen.blit(speed_text, (10, 10))

        pygame.display.flip()

    def run(self) -> None:
        """Run the GUI simulation loop."""
        try:
            while self.running:
                self.handle_events()
                if not self.settings.paused:
                    self.simulator.next_generation()
                self.draw()
                self.clock.tick(self.settings.fps)
        finally:
            pygame.quit()


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Life Cell Simulator")
    parser.add_argument(
        "--rows", type=int, default=20, help="Number of rows in the grid"
    )
    parser.add_argument(
        "--cols", type=int, default=30, help="Number of columns in the grid"
    )
    parser.add_argument(
        "--cell_size",
        type=int,
        default=20,
        help="Size of each cell in pixels (GUI only)",
    )
    parser.add_argument("--gui", action="store_true", help="Force graphical mode (GUI)")
    parser.add_argument(
        "--text", action="store_true", help="Force text-only mode (CLI)"
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the Life Cell Simulator."""
    args = parse_arguments()
    simulator = LifeSimulator(args.rows, args.cols)

    if args.text or not PYGAME_AVAILABLE:
        if not PYGAME_AVAILABLE and args.gui:
            print("Pygame not available. Falling back to text-only mode.")
        print("Running in text-only mode.")
        interface = TextInterface(simulator)
    else:
        try:
            print("Running in graphical mode.")
            interface = GUIInterface(simulator, args.cell_size)
        except pygame.error as exc:
            print(f"Failed to start graphical mode: {exc}")
            print("Falling back to text-only mode.")
            interface = TextInterface(simulator)

    interface.run()


if __name__ == "__main__":
    main()
