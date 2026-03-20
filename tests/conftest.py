"""pytest configuration for QNG test suite."""
import sys
from pathlib import Path

# Ensure scripts/ is on the path for all tests
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
