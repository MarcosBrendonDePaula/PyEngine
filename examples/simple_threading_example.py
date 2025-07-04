import multiprocessing as mp
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.component import Component

class SimpleMovementComponent(Component):
    """Simple component for demonstration."""
    
    def __init__(self, speed=50.0):
        super().__init__()
        self.speed = speed
        self.direction = 1
        
    def update(self):
        if not self.entity:
            return
            
        # Simple movement with bouncing
        self.entity.position.x += self.direction * self.speed * self.entity.delta_time
        
        # Bounce off screen edges
        if self.entity.position.x > 800 or self.entity.position.x < 0:
            self.direction *= -1

class SimpleThreadingScene(BaseScene):
    """Simple scene demonstrating threaded entity updates."""
    
    def on_initialize(self):
        print("Creating entities for threading demonstration...")
        
        # Create many entities to demonstrate threading benefits
        for i in range(500):
            entity = Entity(x=400, y=50 + i)
            movement = SimpleMovementComponent(speed=100 + i % 100)
            entity.add_component(movement)
            self.add_entity(entity)
            
        print(f"Created {len(self.entities)} entities")

def main():
    cpu_count = mp.cpu_count()
    print(f"System has {cpu_count} CPU cores")
    
    num_threads = max(1, int(cpu_count * 0.75))
    print(f"Using {num_threads} threads for processing")

    engine = create_engine(
        title="PyEngine Simple Threading Demo",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    demo_scene = SimpleThreadingScene()
    engine.set_scene("simple_threading_demo", demo_scene)
    
    engine.run()

if __name__ == "__main__":
    main()