"""Checkpoint 5 entry point: python bench.py."""
import sys

from scripts.benchmark_personal import run


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    run()
