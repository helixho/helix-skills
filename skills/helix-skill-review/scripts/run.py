#!/usr/bin/env python3
"""Entrypoint for helix-skill-review. Reads one JSON request on stdin, writes one JSON result."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from helix_skill_kit.eval_entry import main

if __name__ == "__main__":
    sys.exit(main())
