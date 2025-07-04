"""
System for launching PyEngine examples
"""

import os
import sys
import subprocess
import threading
from typing import Dict, List, Optional, NamedTuple
from pathlib import Path

class ExampleInfo(NamedTuple):
    """Information about a PyEngine example."""
    name: str
    description: str
    file_path: str
    category: str
    difficulty: str  # "Beginner", "Intermediate", "Advanced"
    features: List[str]
    threading_demo: bool = False

class ExampleLauncher:
    """Handles discovery and launching of PyEngine examples."""
    
    def __init__(self):
        self.examples: Dict[str, ExampleInfo] = {}
        self.categories: Dict[str, List[str]] = {}
        self.base_path = Path(__file__).parent.parent.parent  # Go to examples root
        self._discover_examples()
        
    def _discover_examples(self):
        """Discover all available examples."""
        # Define examples manually for better control and descriptions
        examples_data = [
            ExampleInfo(
                name="Threading Demo",
                description="Demonstrates parallel entity updates with performance monitoring",
                file_path="threading_demo/threading_demo.py",
                category="Performance",
                difficulty="Advanced",
                features=["Multi-threading", "Performance Metrics", "Entity Physics"],
                threading_demo=True
            ),
            ExampleInfo(
                name="Collision Demo",
                description="Interactive collision detection and physics simulation",
                file_path="collider_demo/scenes/collider_demo_scene.py",
                category="Physics",
                difficulty="Intermediate",
                features=["Collision Detection", "Physics", "Interactive Controls"]
            ),
            ExampleInfo(
                name="UI Demo",
                description="Complete user interface components showcase",
                file_path="ui_demo/scenes/ui_demo_scene.py",
                category="User Interface",
                difficulty="Beginner",
                features=["UI Components", "Buttons", "Labels", "Interactive Elements"]
            ),
            ExampleInfo(
                name="Light Demo",
                description="Dynamic lighting and shadow effects",
                file_path="light_demo/scenes/light_demo_scene.py",
                category="Graphics",
                difficulty="Intermediate",
                features=["Dynamic Lighting", "Shadows", "Visual Effects"]
            ),
            ExampleInfo(
                name="Directional Light",
                description="Advanced directional lighting with obstacles",
                file_path="directional_light_demo/scenes/directional_light_scene.py",
                category="Graphics",
                difficulty="Advanced",
                features=["Directional Lighting", "Light Obstacles", "Ray Casting"]
            ),
            ExampleInfo(
                name="Sprite Animation",
                description="Sprite sheet animations and character movement",
                file_path="sprite_animation_demo/scenes/sprite_animation_demo.py",
                category="Animation",
                difficulty="Beginner",
                features=["Sprite Sheets", "Animation", "Character Movement"]
            ),
            ExampleInfo(
                name="Day/Night Cycle",
                description="Dynamic day and night cycle simulation",
                file_path="day_night_cycle_demo/scenes/day_night_cycle_scene.py",
                category="Simulation",
                difficulty="Intermediate",
                features=["Time Simulation", "Dynamic Environment", "Celestial Bodies"]
            ),
            ExampleInfo(
                name="State Machine Timer",
                description="State management and timer components",
                file_path="state_timer_demo/scenes/state_timer_demo_scene.py",
                category="Game Logic",
                difficulty="Intermediate",
                features=["State Machines", "Timers", "Component System"]
            ),
            ExampleInfo(
                name="Water Particle Demo",
                description="Fluid simulation with particle systems",
                file_path="water_particle_demo/scenes/water_particle_scene.py",
                category="Physics",
                difficulty="Advanced",
                features=["Particle Systems", "Fluid Simulation", "Advanced Physics"]
            ),
            ExampleInfo(
                name="Local Multiplayer",
                description="Local multiplayer game mechanics",
                file_path="local_multiplayer_game/Local_Multiplayer_Game.py",
                category="Multiplayer",
                difficulty="Advanced",
                features=["Local Multiplayer", "Game Mechanics", "Player Management"]
            ),
            ExampleInfo(
                name="Puzzle Game",
                description="Shape-based puzzle game with collision detection",
                file_path="puzlegame/scenes/puzzle_scene.py",
                category="Games",
                difficulty="Intermediate",
                features=["Puzzle Mechanics", "Shape Collision", "Game Logic"]
            ),
            ExampleInfo(
                name="Simple Threading",
                description="Basic threading example for beginners",
                file_path="simple_threading_example.py",
                category="Performance",
                difficulty="Beginner",
                features=["Basic Threading", "Simple Physics", "Educational"],
                threading_demo=True
            ),
            ExampleInfo(
                name="Project Template",
                description="Template structure for new PyEngine projects",
                file_path="project_template/main.py",
                category="Templates",
                difficulty="Beginner",
                features=["Project Structure", "Template", "Best Practices"]
            )
        ]
        
        # Organize examples
        for example in examples_data:
            self.examples[example.name] = example
            
            # Group by category
            if example.category not in self.categories:
                self.categories[example.category] = []
            self.categories[example.category].append(example.name)
            
    def get_examples_by_category(self, category: str) -> List[ExampleInfo]:
        """Get all examples in a specific category."""
        if category not in self.categories:
            return []
        return [self.examples[name] for name in self.categories[category]]
    
    def get_all_categories(self) -> List[str]:
        """Get list of all available categories."""
        return sorted(self.categories.keys())
    
    def get_example(self, name: str) -> Optional[ExampleInfo]:
        """Get specific example by name."""
        return self.examples.get(name)
    
    def get_all_examples(self) -> List[ExampleInfo]:
        """Get all available examples."""
        return list(self.examples.values())
    
    def launch_example(self, example_name: str) -> bool:
        """Launch an example in a separate process."""
        example = self.get_example(example_name)
        if not example:
            print(f"Example '{example_name}' not found")
            return False
            
        # Build full path
        example_path = self.base_path / example.file_path
        
        if not example_path.exists():
            print(f"Example file not found: {example_path}")
            return False
            
        print(f"Launching {example_name}...")
        print(f"Path: {example_path}")
        
        try:
            # Launch in separate process
            def run_example():
                try:
                    # Change to example directory
                    example_dir = example_path.parent
                    original_cwd = os.getcwd()
                    os.chdir(example_dir)
                    
                    # Add parent directories to Python path
                    env = os.environ.copy()
                    python_path = str(self.base_path.parent)  # Add engine root
                    if 'PYTHONPATH' in env:
                        env['PYTHONPATH'] = f"{python_path}:{env['PYTHONPATH']}"
                    else:
                        env['PYTHONPATH'] = python_path
                    
                    # Execute the example
                    result = subprocess.run(
                        [sys.executable, example_path.name],
                        cwd=example_dir,
                        env=env,
                        capture_output=False
                    )
                    
                    # Restore directory
                    os.chdir(original_cwd)
                    
                    if result.returncode == 0:
                        print(f"✓ {example_name} completed successfully")
                    else:
                        print(f"✗ {example_name} exited with code {result.returncode}")
                        
                except Exception as e:
                    print(f"✗ Error launching {example_name}: {e}")
                    os.chdir(original_cwd)
            
            # Run in background thread to not block the launcher
            thread = threading.Thread(target=run_example, daemon=True)
            thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to launch {example_name}: {e}")
            return False
    
    def get_example_stats(self) -> Dict[str, int]:
        """Get statistics about available examples."""
        stats = {
            "total": len(self.examples),
            "categories": len(self.categories),
            "beginner": 0,
            "intermediate": 0,
            "advanced": 0,
            "threading_demos": 0
        }
        
        for example in self.examples.values():
            if example.difficulty == "Beginner":
                stats["beginner"] += 1
            elif example.difficulty == "Intermediate":
                stats["intermediate"] += 1
            elif example.difficulty == "Advanced":
                stats["advanced"] += 1
                
            if example.threading_demo:
                stats["threading_demos"] += 1
                
        return stats