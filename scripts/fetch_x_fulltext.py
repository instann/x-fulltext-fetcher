#!/usr/bin/env python3
"""Repository-local wrapper for the x-fulltext-fetch CLI."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from x_fulltext_fetcher.fetch import main


if __name__ == "__main__":
    raise SystemExit(main())
