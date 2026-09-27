#!/data/data/com.termux/files/usr/bin/python3
import sys
import os

# Insert current directory into path to allow imports from sutra_agent_core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp.server.fastmcp import FastMCP
from sutra_agent_core import obsidian_brain_search

# Initialize FastMCP Server
mcp = FastMCP("SutraSecondBrain")

@mcp.tool
def search_second_brain(query: str) -> str:
    """
    Search Ashutosh Singh's Obsidian Second Brain / personal knowledge vault.
    This contains notes, philosophy, blueprints, creator strategies, and systems engineering blueprints
    for projects like Anant Anaadi, Poly bhai, turiya.world, Chiransh, etc.
    """
    return obsidian_brain_search(query)

if __name__ == "__main__":
    mcp.run()
