import multiprocessing as mp
from engine import create_engine
from scenes.ui_demo_scene import UIDemoScene

def main():
    # Get CPU cores for processing
    cpu_count = mp.cpu_count()
    num_threads = max(1, int(cpu_count * 0.75))
    
    # Create engine
    engine = create_engine(
        title="PyEngine UI Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    # If your engine supports scene manager access, you can also do:
    # scene_manager = engine.get_scene_manager()  # or however you access it
    # scene_manager.add_scene("ui_demo", UIDemoScene())
    # scene_manager.set_scene("ui_demo", transition=False)
    
    # But the recommended way with your engine pattern is:
    ui_demo_scene = UIDemoScene()
    engine.set_scene("ui_demo", ui_demo_scene)
    
    # Run game
    engine.run()

if __name__ == "__main__":
    main()