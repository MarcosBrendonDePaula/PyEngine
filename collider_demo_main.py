import multiprocessing as mp
from engine import create_engine
from scenes.collider_demo_scene import ColliderDemoScene

def main():
    # Get the number of CPU cores
    cpu_count = mp.cpu_count()
    print(f"System has {cpu_count} CPU cores")
    
    # Use 75% of available cores (minimum 1)
    num_threads = max(1, int(cpu_count * 0.75))
    print(f"Using {num_threads} threads for processing")

    # Create the engine with specified thread count
    print("Creating engine")
    engine = create_engine(
        title="PyEngine Collider Types Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    # Create and set the collider demo scene
    print("Creating collider demo scene")
    demo_scene = ColliderDemoScene()
    
    # Add and set the scene
    print("Adding collider demo scene to engine")
    engine.set_scene("collider_demo", demo_scene)
    
    # Start the game
    print("Starting game")
    engine.run()

if __name__ == "__main__":
    main()
