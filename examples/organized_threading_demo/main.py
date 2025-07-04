"""
PyEngine Advanced Threading Demo
Demonstrates threading with advanced features and comprehensive monitoring
"""

import multiprocessing as mp
from engine import create_engine
from scenes.threading_demo_scene import ThreadingDemoScene

def main():
    """Main entry point for the threading demonstration."""
    print("PyEngine Threading Demo")
    print("=======================")
    
    # System information
    cpu_count = mp.cpu_count()
    print(f"System has {cpu_count} CPU cores")
    
    # Configure threading
    num_threads = max(1, int(cpu_count * 0.75))
    print(f"Using {num_threads} threads for processing")
    
    # Get user preferences
    entity_count = _get_entity_count()
    
    print(f"\nConfiguration:")
    print(f"  - Entities: {entity_count}")
    print(f"  - Threads: {num_threads}")
    print(f"  - Threading: {'Enabled' if num_threads > 1 else 'Disabled'}")
    
    # Create engine with optimized threading
    engine = create_engine(
        title=f"PyEngine Threading Demo - {entity_count} entities ({num_threads} threads)",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    # Create and configure scene
    demo_scene = ThreadingDemoScene(entity_count=entity_count)
    engine.set_scene("threading_demo", demo_scene)
    
    # Display instructions
    _show_instructions()
    
    # Run the demo
    try:
        print("\nStarting demo...")
        engine.run()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError during demo: {e}")
    finally:
        engine.shutdown()
        print("Demo completed successfully")

def _get_entity_count() -> int:
    """Get entity count from user input with validation."""
    while True:
        try:
            user_input = input("\nNumber of entities (default 1000, max 5000): ").strip()
            if not user_input:
                return 1000
                
            entity_count = int(user_input)
            if entity_count < 10:
                print("Minimum 10 entities required")
                continue
            elif entity_count > 5000:
                print("Maximum 5000 entities allowed for performance")
                continue
                
            return entity_count
            
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nUsing default: 1000 entities")
            return 1000

def _show_instructions():
    """Display usage instructions."""
    print("\nControls:")
    print("  ESC or close window - Exit demo")
    print("  Watch performance metrics in top-left corner")
    print("\nFeatures:")
    print("  - Entities move with realistic physics")
    print("  - Bouncing off screen edges")
    print("  - Random direction changes")
    print("  - Visual pulse effects")
    print("  - Real-time performance monitoring")
    
    if mp.cpu_count() > 1:
        print("  - Multi-threaded entity updates")
    else:
        print("  - Single-threaded processing (1 CPU core)")

if __name__ == "__main__":
    main()