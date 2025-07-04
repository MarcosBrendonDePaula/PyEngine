#!/usr/bin/env python3
"""
PyEngine Examples Launcher
Script principal para acessar todos os exemplos do PyEngine
"""

import os
import sys
from pathlib import Path

def main():
    """Launch the PyEngine examples menu."""
    print("PyEngine Examples Launcher")
    print("=" * 30)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    launcher_path = project_root / "examples" / "launcher_menu"
    
    # Check if launcher exists
    if not launcher_path.exists():
        print("❌ Error: Launcher menu not found!")
        print(f"Expected location: {launcher_path}")
        return 1
    
    # Add launcher to Python path
    sys.path.insert(0, str(launcher_path))
    
    # Change to launcher directory
    original_cwd = os.getcwd()
    os.chdir(launcher_path)
    
    try:
        # Import and run the launcher
        from main import main as launcher_main
        print("🚀 Starting PyEngine Examples Launcher...")
        print("")
        launcher_main()
        
    except ImportError as e:
        print(f"❌ Error importing launcher: {e}")
        print("Make sure the PyEngine is properly installed.")
        return 1
        
    except Exception as e:
        print(f"❌ Error running launcher: {e}")
        return 1
        
    finally:
        # Restore original directory
        os.chdir(original_cwd)
        
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)