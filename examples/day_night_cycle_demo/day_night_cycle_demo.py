import pygame
from engine.core.scenes.scene_manager import SceneManager
from scenes.day_night_cycle_scene import DayNightCycleScene

import multiprocessing as mp
from engine import create_engine

def main():
    # Get CPU cores for processing
    cpu_count = mp.cpu_count()
    num_threads = max(1, int(cpu_count * 0.75))
    
    # Create engine
    engine = create_engine(
        title="Day/Night Cycle Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )

    # Create and set scene
    scene = DayNightCycleScene()
    engine.set_scene("light_demo", scene)
    
    # Run game
    engine.run()

if __name__ == "__main__":
    main()