"""
Main entry point for the AI Agent system.
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from ai_agent.cli.main import main as cli_main
from ai_agent.web.server import WebServer


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="ai-agent",
        description="Local AI Agent - A powerful local AI assistant"
    )
    
    parser.add_argument(
        "--mode",
        choices=["cli", "web"],
        default="cli",
        help="Run mode: cli or web (default: cli)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for web server (default: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for web server (default: 8080)"
    )
    
    args, remaining = parser.parse_known_args()
    
    if args.mode == "web":
        # Run web server
        print(f"Starting web server on http://{args.host}:{args.port}")
        server = WebServer(host=args.host, port=args.port)
        server.run()
    else:
        # Run CLI
        sys.argv = [sys.argv[0]] + remaining
        cli_main()


if __name__ == "__main__":
    main()