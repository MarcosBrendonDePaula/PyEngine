import multiprocessing as mp
from engine import create_engine
from scenes.resource_cache_demo_scene import ResourceCacheDemoScene

def main():
    # Get CPU cores for processing
    cpu_count = mp.cpu_count()
    num_threads = max(1, int(cpu_count * 0.75))
    
    # Create engine
    engine = create_engine(
        title="Resource Cache Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    # Create and set scene
    scene = ResourceCacheDemoScene()
    engine.set_scene("resource_cache_demo", scene)
    
    # Run game
    engine.run()

if __name__ == "__main__":
    main()
