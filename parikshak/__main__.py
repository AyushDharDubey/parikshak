"""
Parikshak: records answers, flags and time per question with a live
countdown, autosave/resume, and CSV export.

Usage:
    python -m parikshak                        # prompts for setup
    python -m parikshak -n 120 -m 120          # 120 questions, 120 minutes
    python -m parikshak --state paper2.json    # separate save file
    python -m parikshak --no-color             # plain output (or set NO_COLOR)
"""
from .app import main

if __name__ == "__main__":
    main()
