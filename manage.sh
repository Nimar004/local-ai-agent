#!/bin/bash
cd "$(dirname "$0")"
case "${1:-help}" in
    start) echo "Starting CLI mode..."; source venv/bin/activate; python src/main.py interactive ;;
    start-web) echo "Starting Web mode..."; source venv/bin/activate; python src/main.py --mode web --port 8080 ;;
    stop) echo "Stopping..."; pkill -f "python src/main.py" || true; echo "Stopped" ;;
    status) echo "=== Status ==="; pgrep -x "ollama" > /dev/null && echo "✓ Ollama: Running" || echo "✗ Ollama: Stopped"; ollama list 2>/dev/null; pgrep -f "python src/main.py" > /dev/null && echo "✓ AI Agent: Running" || echo "✗ AI Agent: Stopped" ;;
    models) ollama list ;;
    help|*) echo "Usage: $0 {start|start-web|stop|status|models|help}" ;;
esac
