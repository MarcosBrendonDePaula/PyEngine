import multiprocessing as mp
from engine import create_engine
from scenes.directional_light_demo import DirectionalLightDemo

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
        title="PyEngine Directional Light Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    # Create and set the directional light demo scene
    print("Creating directional light demo scene")
    demo_scene = DirectionalLightDemo()
    
    # Add and set the scene
    print("Adding directional light demo scene to engine")
    engine.set_scene("directional_light_demo", demo_scene)
    
    # Start the game
    print("Starting game")
    engine.run()

if __name__ == "__main__":
    main()
