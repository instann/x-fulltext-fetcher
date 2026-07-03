#!/usr/bin/env python3
"""Run the local X Fulltext Fetcher app from a source checkout."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from x_fulltext_fetcher.app import main


if __name__ == "__main__":
    raise SystemExit(main())
