"""
PyEngine Examples Launcher
Menu principal para navegar e executar todos os exemplos do PyEngine
"""

import multiprocessing as mp
from engine import create_engine
from scenes.main_menu_scene import MainMenuScene

def main():
    """Launcher principal dos exemplos PyEngine."""
    print("PyEngine Examples Launcher")
    print("==========================")
    
    cpu_count = mp.cpu_count()
    print(f"System has {cpu_count} CPU cores")
    
    num_threads = max(1, int(cpu_count * 0.75))
    print(f"Using {num_threads} threads for processing")

    engine = create_engine(
        title="PyEngine Examples Launcher",
        width=1200,
        height=800,
        num_threads=num_threads
    )
    
    main_menu_scene = MainMenuScene()
    engine.set_scene("main_menu", main_menu_scene)
    
    print("Starting launcher...")
    engine.run()

if __name__ == "__main__":
    main()