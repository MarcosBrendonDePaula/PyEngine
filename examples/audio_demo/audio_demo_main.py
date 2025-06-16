import multiprocessing as mp
from engine import create_engine
from scenes.audio_demo_scene import AudioDemoScene

def main():
    # Get CPU cores for processing
    cpu_count = mp.cpu_count()
    num_threads = max(1, int(cpu_count * 0.75))
    print(num_threads)
    # Create engine
    engine = create_engine(
        title="Positional Audio Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    # Create and set scene
    scene = AudioDemoScene()
    engine.set_scene("audio_demo", scene)
    
    # Run game
    engine.run()

if __name__ == "__main__":
    main()