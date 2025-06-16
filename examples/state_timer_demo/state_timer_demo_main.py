import multiprocessing as mp
from engine import create_engine
from scenes.state_timer_demo_scene import StateTimerDemoScene

def main():
    cpu_count = mp.cpu_count()
    print(f"System has {cpu_count} CPU cores")
    
    num_threads = max(1, int(cpu_count * 0.75))
    print(f"Using {num_threads} threads for processing")

    engine = create_engine(
        title="PyEngine State Machine & Timer Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    demo_scene = StateTimerDemoScene()
    engine.set_scene("state_timer_demo", demo_scene)
    
    engine.run()

if __name__ == "__main__":
    main()


