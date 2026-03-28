"""
Main CLI interface for the AI Agent system.
"""

import asyncio
import argparse
import sys
import json
from typing import List, Optional

from ..core.agent import AIAgent, AgentConfig, AgentMode


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="ai-agent",
        description="Local AI Agent - A powerful local AI assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-agent ask "What is Python?"
  ai-agent code "Create a function to sort a list"
  ai-agent models list
  ai-agent analyze file.txt
  ai-agent web "https://example.com"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a question to the AI")
    ask_parser.add_argument("question", help="The question to ask")
    ask_parser.add_argument("-m", "--model", help="Specific model to use")
    ask_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Code command
    code_parser = subparsers.add_parser("code", help="Generate code")
    code_parser.add_argument("description", help="Description of the code to generate")
    code_parser.add_argument("-l", "--language", default="python", help="Programming language")
    code_parser.add_argument("-m", "--model", help="Specific model to use")
    code_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a file")
    analyze_parser.add_argument("file", help="File to analyze")
    analyze_parser.add_argument("-t", "--type", default="general", help="Type of analysis")
    analyze_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Models command
    models_parser = subparsers.add_parser("models", help="Manage models")
    models_subparsers = models_parser.add_subparsers(dest="models_command")
    
    # Models list
    models_subparsers.add_parser("list", help="List available models")
    
    # Models info
    models_info_parser = models_subparsers.add_parser("info", help="Get model info")
    models_info_parser.add_argument("model_name", help="Name of the model")
    
    # Web command
    web_parser = subparsers.add_parser("web", help="Access a website")
    web_parser.add_argument("url", help="URL to access")
    web_parser.add_argument("-a", "--action", default="fetch", help="Action to perform")
    web_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Screen command
    screen_parser = subparsers.add_parser("screen", help="Control screen")
    screen_parser.add_argument("action", help="Action to perform")
    screen_parser.add_argument("-t", "--target", help="Target element")
    screen_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Interactive mode
    subparsers.add_parser("interactive", help="Start interactive mode")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    
    return parser


async def handle_ask(args: argparse.Namespace, agent: AIAgent) -> None:
    """Handle the ask command."""
    result = await agent.execute_task(args.question, args.model)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(result["response"])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)


async def handle_code(args: argparse.Namespace, agent: AIAgent) -> None:
    """Handle the code command."""
    result = await agent.generate_code(args.description, args.language, args.model)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(result["response"])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)


async def handle_analyze(args: argparse.Namespace, agent: AIAgent) -> None:
    """Handle the analyze command."""
    result = await agent.analyze_file(args.file, args.type)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(result["response"])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)


async def handle_models(args: argparse.Namespace, agent: AIAgent) -> None:
    """Handle the models command."""
    if args.models_command == "list":
        models = await agent.list_available_models()
        print(json.dumps(models, indent=2))
    elif args.models_command == "info":
        info = await agent.get_model_info(args.model_name)
        print(json.dumps(info, indent=2))
    else:
        print("Please specify a models subcommand (list, info)", file=sys.stderr)
        sys.exit(1)


async def handle_web(args: argparse.Namespace, agent: AIAgent) -> None:
    """Handle the web command."""
    result = await agent.access_web(args.url, args.action)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(result["response"])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)


async def handle_screen(args: argparse.Namespace, agent: AIAgent) -> None:
    """Handle the screen command."""
    result = await agent.control_screen(args.action, args.target)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(result["response"])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)


async def handle_interactive(agent: AIAgent) -> None:
    """Handle interactive mode."""
    print("AI Agent Interactive Mode")
    print("Type 'exit' or 'quit' to exit")
    print("Type 'help' for available commands")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            if user_input.lower() == "help":
                print("""
Available commands:
  ask <question>     - Ask a question
  code <description> - Generate code
  analyze <file>     - Analyze a file
  models list        - List available models
  web <url>          - Access a website
  help               - Show this help
  exit/quit          - Exit interactive mode
                """)
                continue
                
            # Parse the command
            parts = user_input.split(maxsplit=1)
            if not parts:
                continue
                
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if cmd == "ask":
                if not arg:
                    print("Please provide a question")
                    continue
                result = await agent.execute_task(arg)
                if result.get("success"):
                    print(result["response"])
                else:
                    print(f"Error: {result.get('error')}")
                    
            elif cmd == "code":
                if not arg:
                    print("Please provide a description")
                    continue
                result = await agent.generate_code(arg)
                if result.get("success"):
                    print(result["response"])
                else:
                    print(f"Error: {result.get('error')}")
                    
            elif cmd == "analyze":
                if not arg:
                    print("Please provide a file path")
                    continue
                result = await agent.analyze_file(arg)
                if result.get("success"):
                    print(result["response"])
                else:
                    print(f"Error: {result.get('error')}")
                    
            elif cmd == "models":
                if arg == "list":
                    models = await agent.list_available_models()
                    for model in models:
                        print(f"- {model['name']} ({model['backend']})")
                else:
                    print("Unknown models command. Use 'models list'")
                    
            elif cmd == "web":
                if not arg:
                    print("Please provide a URL")
                    continue
                result = await agent.access_web(arg)
                if result.get("success"):
                    print(result["response"])
                else:
                    print(f"Error: {result.get('error')}")
                    
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


async def handle_config(agent: AIAgent) -> None:
    """Handle the config command."""
    config = {
        "mode": agent.config.mode.value,
        "default_model": agent.config.default_model,
        "max_concurrent_tasks": agent.config.max_concurrent_tasks,
        "enable_screen_control": agent.config.enable_screen_control,
        "enable_web_access": agent.config.enable_web_access,
        "enable_file_access": agent.config.enable_file_access,
        "cache_enabled": agent.config.cache_enabled,
        "log_level": agent.config.log_level
    }
    print(json.dumps(config, indent=2))


async def main_async(args: List[str]) -> None:
    """Main async function."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return
        
    # Create agent
    config = AgentConfig(mode=AgentMode.CLI)
    agent = AIAgent(config)
    
    try:
        await agent.initialize()
        
        # Handle commands
        if parsed_args.command == "ask":
            await handle_ask(parsed_args, agent)
        elif parsed_args.command == "code":
            await handle_code(parsed_args, agent)
        elif parsed_args.command == "analyze":
            await handle_analyze(parsed_args, agent)
        elif parsed_args.command == "models":
            await handle_models(parsed_args, agent)
        elif parsed_args.command == "web":
            await handle_web(parsed_args, agent)
        elif parsed_args.command == "screen":
            await handle_screen(parsed_args, agent)
        elif parsed_args.command == "interactive":
            await handle_interactive(agent)
        elif parsed_args.command == "config":
            await handle_config(agent)
        else:
            parser.print_help()
            
    finally:
        await agent.shutdown()


def main() -> None:
    """Main entry point for the CLI."""
    asyncio.run(main_async(sys.argv[1:]))


def cli() -> None:
    """CLI entry point (alias for main)."""
    main()


if __name__ == "__main__":
    main()