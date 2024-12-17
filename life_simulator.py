import os
import time
import random
import argparse
import sys
import select
import termios
import tty

# Optional: Try to import Pygame. If unavailable, set a fallback flag.
try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


def is_key_pressed():
    """Check if a key was pressed without blocking."""
    if sys.platform != "win32":
        # Unix-like systems
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None
    else:
        # Windows systems
        import msvcrt

        if msvcrt.kbhit():
            return msvcrt.getch().decode("utf-8")
        return None


def add_random_cell(grid):
    """Add a live cell at a random location."""
    rows, cols = len(grid), len(grid[0])
    x, y = random.randint(0, rows - 1), random.randint(0, cols - 1)
    grid[x][y] = 1
    return grid


# CLI Text-Only Version
def run_text_mode(rows, cols, speed):
    """Run the simulation in text-only mode with interactive controls."""
    grid = create_grid(rows, cols, randomize=True)  # Always start with random grid
    paused = False

    # Set up terminal for non-blocking input
    if sys.platform != "win32":
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())

            while True:
                os.system("cls" if os.name == "nt" else "clear")
                for row in grid:
                    print("".join("#" if cell else "." for cell in row))
                print("\nControls:")
                print("Space: Pause/Resume")
                print("Enter: Add random cell")
                print("Ctrl+C: Exit")
                print(f"Status: {'Paused' if paused else 'Running'}")

                # Check for key press
                key = is_key_pressed()
                if key == " ":
                    paused = not paused
                elif key == "\n":
                    grid = add_random_cell(grid)

                if not paused:
                    grid = next_generation(grid)
                time.sleep(speed)

        except KeyboardInterrupt:
            print("\nSimulation ended.")
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    else:
        # Windows version
        try:
            while True:
                os.system("cls")
                for row in grid:
                    print("".join("#" if cell else "." for cell in row))
                print("\nControls:")
                print("Space: Pause/Resume")
                print("Enter: Add random cell")
                print("Ctrl+C: Exit")
                print(f"Status: {'Paused' if paused else 'Running'}")

                key = is_key_pressed()
                if key == " ":
                    paused = not paused
                elif key == "\r":  # Windows uses \r for Enter
                    grid = add_random_cell(grid)

                if not paused:
                    grid = next_generation(grid)
                time.sleep(speed)

        except KeyboardInterrupt:
            print("\nSimulation ended.")


# Common Grid Functions
def create_grid(rows, cols, randomize=False):
    """Initialize the grid with dead cells or random live cells."""
    if randomize:
        return [[random.choice([0, 1]) for _ in range(cols)] for _ in range(rows)]
    return [[0 for _ in range(cols)] for _ in range(rows)]


def count_neighbors(grid, x, y):
    """Count the live neighbors around a cell."""
    rows, cols = len(grid), len(grid[0])
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    count = 0
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < rows and 0 <= ny < cols:
            count += grid[nx][ny]
    return count


def next_generation(grid):
    """Compute the next state of the grid based on Conway's rules."""
    rows, cols = len(grid), len(grid[0])
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for x in range(rows):
        for y in range(cols):
            neighbors = count_neighbors(grid, x, y)
            if grid[x][y] == 1:
                # Survival: 2 or 3 neighbors
                new_grid[x][y] = 1 if neighbors in (2, 3) else 0
            else:
                # Birth: exactly 3 neighbors
                new_grid[x][y] = 1 if neighbors == 3 else 0
    return new_grid


# Pygame GUI Version
def run_gui_mode(rows, cols, cell_size, speed):
    """Run the simulation with Pygame graphical interface."""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    ALIVE_COLOR = (50, 205, 50)  # Green for alive cells
    DEAD_COLOR = (30, 30, 30)  # Dark gray for dead cells

    width, height = cols * cell_size, rows * cell_size

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()

    grid = create_grid(rows, cols, randomize=True)

    running = True
    paused = False

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    grid = create_grid(rows, cols, randomize=True)
                elif event.key == pygame.K_c:
                    grid = create_grid(rows, cols)
                elif event.key == pygame.K_UP:
                    speed = max(1, speed - 1)
                elif event.key == pygame.K_DOWN:
                    speed += 1

        if not paused:
            grid = next_generation(grid)

        for x in range(rows):
            for y in range(cols):
                color = ALIVE_COLOR if grid[x][y] == 1 else DEAD_COLOR
                pygame.draw.rect(
                    screen, color, (y * cell_size, x * cell_size, cell_size, cell_size)
                )

        pygame.display.flip()
        clock.tick(speed)

    pygame.quit()


# Main Function to Choose Mode
def main():
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
    parser.add_argument(
        "--speed",
        type=float,
        default=0.05,
        help="Time (in seconds) between updates (CLI only)",
    )
    parser.add_argument("--gui", action="store_true", help="Force graphical mode (GUI)")
    parser.add_argument(
        "--text", action="store_true", help="Force text-only mode (CLI)"
    )
    args = parser.parse_args()

    if args.text or not PYGAME_AVAILABLE:
        if not PYGAME_AVAILABLE and args.gui:
            print("Pygame not available. Falling back to text-only mode.")
        print("Running in text-only mode.")
        run_text_mode(args.rows, args.cols, args.speed)  # Remove randomize parameter
    else:
        try:
            print("Running in graphical mode.")
            run_gui_mode(args.rows, args.cols, args.cell_size, 10)
        except Exception as e:
            print(f"Failed to start graphical mode: {e}")
            print("Falling back to text-only mode.")
            run_text_mode(
                args.rows, args.cols, args.speed
            )


if __name__ == "__main__":
    main()
