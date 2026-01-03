#!/usr/bin/env python3
"""Wrapper script to run the GLM MCP server with proper imports."""
import sys
import os

# Add the server directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up the API key from environment
if not os.environ.get("ZAI_API_KEY"):
    # Try to read from .env file
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("ZAI_API_KEY="):
                    os.environ["ZAI_API_KEY"] = line.strip().split("=", 1)[1].strip('"\'')
                    break

from server import mcp
mcp.run()
