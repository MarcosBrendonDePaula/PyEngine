import multiprocessing as mp
import pygame
from engine import create_engine
from scenes.simple_resource_scene import SimpleResourceScene

def main():
    # Get CPU cores for processing
    cpu_count = mp.cpu_count()
    num_threads = max(1, int(cpu_count * 0.75))
    
    # Create engine
    engine = create_engine(
        title="Simple Resource Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    # Create and set scene
    scene = SimpleResourceScene()
    engine.set_scene("simple_resource_demo", scene)
    
    # Run game
    engine.run()

if __name__ == "__main__":
    main()
