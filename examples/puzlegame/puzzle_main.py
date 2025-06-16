import multiprocessing as mp
from engine import create_engine
from scenes.puzzle_scene import PuzzleScene


def main():
    # Get CPU cores for processing
    cpu_count = mp.cpu_count()
    num_threads = max(1, int(cpu_count * 0.75))

    # Create engine
    engine = create_engine(
        title="PyEngine Puzzle Game",
        width=800,
        height=600,
        num_threads=num_threads
    )

    # Create and set scene
    scene = PuzzleScene()
    engine.set_scene("puzzle", scene)

    # Run game
    engine.run()


if __name__ == "__main__":
    main()

