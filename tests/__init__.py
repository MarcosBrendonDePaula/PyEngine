import sys
from pathlib import Path
# Ensure project root is on sys.path when running tests
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
