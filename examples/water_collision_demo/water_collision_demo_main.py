import multiprocessing as mp
from engine import create_engine
from scenes.water_collision_scene import WaterCollisionScene

def main():
    # Get CPU cores for processing
    cpu_count = mp.cpu_count()
    num_threads = max(1, int(cpu_count * 0.75))
    
    # Create engine
    engine = create_engine(
        title="Water Collision Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    # Create and set scene
    water_scene = WaterCollisionScene()
    engine.set_scene("water_collision", water_scene)
    
    # Run game
    engine.run()

if __name__ == "__main__":
    main()
