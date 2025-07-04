"""
PyEngine Threading Demo - Main Entry Point
Demonstrates parallel entity updates with performance monitoring
"""

import multiprocessing as mp
from engine import create_engine
from scenes.threading_demo_scene import ThreadingDemoScene

def main():
    """Run the threading demo."""
    print("PyEngine Threading Demo")
    print("=======================")
    
    cpu_count = mp.cpu_count()
    print(f"System has {cpu_count} CPU cores")
    
    num_threads = max(1, int(cpu_count * 0.75))
    print(f"Using {num_threads} threads for processing")

    # Get entity count from user
    try:
        entity_count = int(input("Number of entities (default 1000): ") or "1000")
        entity_count = max(10, min(5000, entity_count))
    except ValueError:
        entity_count = 1000

    engine = create_engine(
        title=f"PyEngine Threading Demo - {entity_count} entities",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    threading_demo_scene = ThreadingDemoScene(entity_count=entity_count)
    engine.set_scene("threading_demo", threading_demo_scene)
    
    print(f"\nStarting demo with {entity_count} entities...")
    print("Controls: ESC to exit, watch performance metrics in top-left")
    
    engine.run()

if __name__ == "__main__":
    main()