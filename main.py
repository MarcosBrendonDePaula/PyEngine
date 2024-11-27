import multiprocessing as mp
from engine import create_engine
from scenes.menu_scene import MenuScene
from scenes.ui_demo_scene import UIDemoScene

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
        title="PyEngine Physics Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    # Create the menu scene
    print("Creating menu scene")
    menu_scene = MenuScene()
    
    # Add and set the scene (this will also set up the interface)
    print("Adding menu scene to engine")
    engine.set_scene("menu", menu_scene)
    
    # Start the game
    print("Starting game")
    engine.run()

if __name__ == "__main__":
    main()
