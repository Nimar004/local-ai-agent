# Local AI Agent

A powerful local AI agent system that runs entirely on your machine. No API keys required!

## Features

- 🤖 **Multiple AI Model Support**: Works with Ollama, LM Studio, and LocalAI
- 💻 **CLI & Web Interface**: Use from command line or beautiful web UI
- 🎯 **Smart Model Selection**: Automatically chooses the best model for each task
- 🔧 **Advanced Tools**:
  - Code generation and analysis
  - Screen control and automation
  - Web browsing and scraping
  - File handling and analysis
  - Video editing capabilities
- 🚀 **Optimized for Mac Mini M4**: Efficient resource usage
- 🔒 **100% Local**: No data leaves your machine

## Quick Start

### Prerequisites

1. **Install Ollama** (recommended):
   ```bash
   brew install ollama
   ollama serve
   ollama pull llama3.2
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Agent

#### CLI Mode
```bash
# Ask a question
python src/main.py ask "What is Python?"

# Generate code
python src/main.py code "Create a function to sort a list" -l python

# Analyze a file
python src/main.py analyze myfile.py

# List available models
python src/main.py models list

# Interactive mode
python src/main.py interactive
```

#### Web Interface Mode
```bash
# Start web server
python src/main.py --mode web --port 8080

# Open in browser: http://localhost:8080
```

## Architecture

```
src/ai_agent/
├── core/                    # Core agent functionality
│   ├── agent.py            # Main agent class
│   ├── model_manager.py    # Model management
│   └── task_executor.py    # Task execution
├── cli/                    # Command-line interface
│   └── main.py            # CLI entry point
├── tools/                  # Agent tools
│   ├── screen_control.py  # Screen automation
│   ├── web_access.py      # Web browsing
│   ├── file_handler.py    # File operations
│   └── video_editor.py    # Video editing
└── web/                    # Web interface
    ├── server.py          # Web server
    └── static/            # Static files
        └── index.html     # Web UI
```

## Supported Models

### Ollama
- llama3.2, llama3.1, llama3
- codellama, codegemma
- mistral, mixtral
- phi3, gemma2
- And many more...

### LM Studio
- Any model compatible with OpenAI API

### LocalAI
- Any GGUF model

## CLI Commands

```bash
# General questions
ai-agent ask "Your question here"

# Code generation
ai-agent code "Description" -l python -m codellama

# File analysis
ai-agent analyze path/to/file.py -t code

# Web access
ai-agent web "https://example.com"

# Screen control
ai-agent screen click --x 100 --y 200

# Model management
ai-agent models list
ai-agent models info llama3.2

# Configuration
ai-agent config

# Interactive mode
ai-agent interactive
```

## Web API

### Execute Task
```bash
POST /api/execute
{
  "task": "Your question",
  "model": "llama3.2",  # optional
  "context": {}         # optional
}
```

### Generate Code
```bash
POST /api/generate
{
  "description": "Function to sort a list",
  "language": "python",
  "model": "codellama"  # optional
}
```

### Analyze File
```bash
POST /api/analyze
{
  "file": "path/to/file.py",
  "type": "code"  # general, code, security, performance
}
```

### List Models
```bash
GET /api/models
```

### WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.send(JSON.stringify({
  action: 'execute',
  task: 'Your question'
}));
```

## Configuration

The agent can be configured via `AgentConfig`:

```python
from ai_agent.core.agent import AgentConfig, AgentMode

config = AgentConfig(
    mode=AgentMode.CLI,
    default_model="llama3.2",
    max_concurrent_tasks=3,
    enable_screen_control=True,
    enable_web_access=True,
    enable_file_access=True,
    cache_enabled=True,
    log_level="INFO"
)
```

## Tools

### Screen Control
- Click, double-click, right-click
- Type text, press keys, hotkeys
- Mouse movement and drag
- Screenshots
- Window management

### Web Access
- Fetch web pages
- Extract text and links
- Browser automation with Selenium
- Form filling
- Screenshots

### File Handler
- Read and write files
- Directory listing
- File search
- File analysis (text, JSON, CSV, code)

### Video Editor
- Trim and merge videos
- Resize and convert formats
- Extract audio
- Speed up/slow down
- Rotate and flip
- Generate thumbnails

## Performance Tips

1. **Use smaller models** for simple tasks
2. **Enable caching** for repeated queries
3. **Close unused models** to free memory
4. **Use GPU acceleration** if available

## Troubleshooting

### Ollama not connecting
```bash
# Check if Ollama is running
ollama list

# Start Ollama server
ollama serve
```

### Screen control not working
```bash
# Install pyautogui
pip install pyautogui pygetwindow pillow

# Grant accessibility permissions on macOS
# System Preferences > Security & Privacy > Accessibility
```

### Video editing not available
```bash
# Install moviepy
pip install moviepy opencv-python
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
flake8 src/
mypy src/
```

## License

MIT License

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## Support

- GitHub Issues: [Report bugs](https://github.com/yourusername/local-ai-agent/issues)
- Documentation: [Wiki](https://github.com/yourusername/local-ai-agent/wiki)

---

Built with ❤️ for the local AI community