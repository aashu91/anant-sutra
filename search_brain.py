#!/data/data/com.termux/files/usr/bin/python3
import sys
import os

# Insert parent directory to system path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sutra_agent_core import obsidian_brain_search

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 search_brain.py <query>")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    results = obsidian_brain_search(query)
    print(results)

if __name__ == "__main__":
    main()
