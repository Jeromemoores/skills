"""Run bundled offline helper and installation checks using only Python stdlib."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "skills/official-stack-dev/scripts"),
               str(ROOT / "skills/official-unreal-dev/scripts"), str(ROOT / "skills/dependency-docs/scripts"), str(ROOT / "tools")]
suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
