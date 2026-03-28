# Local AI Agent - User Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Usage Examples](#usage-examples)
4. [CLI Commands](#cli-commands)
5. [Web Interface](#web-interface)
6. [Management](#management)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### One-Command Setup
```bash
# Download and run setup (installs everything automatically)
chmod +x setup_auto.sh && ./setup_auto.sh
```

### Start Using
```bash
# Option 1: Use alias (works from anywhere)
ai-agent start

# Option 2: Navigate to installation directory
cd ~/ai-agent
./manage.sh start
```

---

## 📦 Installation

### What Gets Installed
- **Ollama**: Local AI model server
- **llama3.2**: Default AI model (2GB)
- **Python dependencies**: All required libraries
- **Management scripts**: Easy start/stop controls
- **Desktop shortcut**: Double-click to manage

### Installation Location
```
~/ai-agent/
├── src/              # Source code
├── venv/             # Python environment
├── logs/             # Log files
├── data/             # Data storage
├── models/           # AI models
├── manage.sh         # Main control script
└── README.md         # Documentation
```

### Custom Installation Path
```bash
# Install to custom location
./setup_auto.sh /path/to/custom/location
```

---

## 💡 Usage Examples

### Example 1: Ask Questions
```bash
ai-agent start
> What is Python?
> Explain machine learning in simple terms
> What are the benefits of local AI?
```

### Example 2: Generate Code
```bash
ai-agent start
> code Create a function to calculate factorial in Python
> code Write a REST API using Flask
> code Build a React component for a todo list
```

### Example 3: Analyze Files
```bash
ai-agent start
> analyze myfile.py
> analyze document.txt
> analyze data.csv
```

### Example 4: Web Interface
```bash
# Start web server
ai-agent start-web

# Open browser to: http://localhost:8080
# Use the beautiful web interface
```

### Example 5: Check Status
```bash
ai-agent status
```

Output:
```
=== Status ===
✓ Ollama: Running
NAME                   ID              SIZE      MODIFIED
llama3.2:3b            a80c4f17acd5    2.0 GB    2 hours ago
mistral:latest         6577803aa9a0    4.4 GB    3 hours ago
✗ AI Agent: Stopped
```

---

## 🖥️ CLI Commands

### Interactive Mode
```bash
ai-agent start
```

Available commands in interactive mode:
- `ask <question>` - Ask a question
- `code <description>` - Generate code
- `analyze <file>` - Analyze a file
- `models list` - List available models
- `help` - Show help
- `exit` - Exit

### Direct Commands
```bash
# Ask a question directly
ai-agent ask "What is Python?"

# Generate code directly
ai-agent code "Create a hello world function"

# Analyze a file directly
ai-agent analyze myfile.py
```

### Model Management
```bash
# List all models
ai-agent models

# Pull a new model
cd ~/ai-agent
./manage.sh pull-model codellama

# Use specific model
ai-agent ask "Explain code" -m codellama
```

---

## 🌐 Web Interface

### Start Web Server
```bash
ai-agent start-web
```

### Access Web Interface
Open your browser to: **http://localhost:8080**

### Web Interface Features
- **Chat Interface**: Ask questions in a beautiful UI
- **Code Generation**: Generate code with syntax highlighting
- **File Analysis**: Upload and analyze files
- **Model Selection**: Choose which AI model to use
- **Real-time Updates**: WebSocket for instant responses

### Web API Endpoints
```bash
# Execute task
POST http://localhost:8080/api/execute
{
  "task": "What is Python?",
  "model": "llama3.2"
}

# Generate code
POST http://localhost:8080/api/generate
{
  "description": "Sort function",
  "language": "python"
}

# List models
GET http://localhost:8080/api/models
```

---

## 🔧 Management

### Start/Stop/Restart
```bash
# Start CLI mode
ai-agent start

# Start Web mode
ai-agent start-web

# Stop everything
ai-agent stop

# Restart
ai-agent restart
```

### Check Status
```bash
ai-agent status
```

### View Logs
```bash
cd ~/ai-agent
./manage.sh logs
```

### Update System
```bash
cd ~/ai-agent
./manage.sh update
```

### Uninstall
```bash
cd ~/ai-agent
./manage.sh uninstall
```

---

## 🛠️ Troubleshooting

### Problem: Ollama not running
```bash
# Check if Ollama is running
pgrep -x "ollama"

# Start Ollama manually
ollama serve

# Or restart everything
ai-agent stop
ai-agent start
```

### Problem: Model not found
```bash
# List available models
ai-agent models

# Pull the model
cd ~/ai-agent
./manage.sh pull-model llama3.2
```

### Problem: Port 8080 already in use
```bash
# Use different port
ai-agent start-web --port 3000

# Or stop conflicting process
lsof -ti:8080 | xargs kill -9
```

### Problem: Python dependencies missing
```bash
cd ~/ai-agent
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Permission denied
```bash
chmod +x ~/ai-agent/manage.sh
chmod +x ~/ai-agent/start.sh
```

### Problem: Command not found: ai-agent
```bash
# Reload shell configuration
source ~/.zshrc

# Or use full path
cd ~/ai-agent
./manage.sh start
```

---

## 📊 Available Models

### Pre-installed Models
- **llama3.2:3b** - General purpose (2GB)
- **mistral:latest** - General purpose (4.4GB)
- **llava:latest** - Vision model (4.7GB)
- **qwen2.5:14b** - Advanced reasoning (9GB)
- **qwen2.5-coder:7b** - Code generation (4.7GB)
- **deepseek-coder:6.7b** - Code specialist (3.8GB)

### Install More Models
```bash
cd ~/ai-agent
./manage.sh pull-model codellama
./manage.sh pull-model phi3
./manage.sh pull-model gemma2
```

---

## 🎯 Tips & Tricks

### 1. Use Aliases for Speed
```bash
# Add to ~/.zshrc
alias ai='ai-agent ask'
alias aic='ai-agent code'

# Then use:
ai "What is Python?"
aic "Create a calculator"
```

### 2. Batch Processing
```bash
# Process multiple files
for file in *.py; do
  ai-agent analyze "$file"
done
```

### 3. Custom System Prompts
```bash
# In interactive mode
> system You are a Python expert. Focus on best practices.
> code Create a web scraper
```

### 4. Export Results
```bash
# Save output to file
ai-agent ask "Explain AI" > explanation.txt
ai-agent code "Sort function" > sort.py
```

---

## 📞 Support

### Get Help
```bash
ai-agent help
cd ~/ai-agent && ./manage.sh help
```

### Check Version
```bash
cd ~/ai-agent
cat README.md | head -20
```

### Report Issues
Check logs at: `~/ai-agent/logs/`

---

## 🔒 Privacy & Security

- **100% Local**: No data leaves your machine
- **No API Keys**: Everything runs locally
- **No Tracking**: Your data stays private
- **Offline Capable**: Works without internet (after initial setup)

---

## 📝 Quick Reference Card

| Command | Description |
|---------|-------------|
| `ai-agent start` | Start CLI mode |
| `ai-agent start-web` | Start web interface |
| `ai-agent stop` | Stop everything |
| `ai-agent status` | Check status |
| `ai-agent models` | List models |
| `ai-agent ask "question"` | Ask question |
| `ai-agent code "description"` | Generate code |
| `ai-agent analyze file` | Analyze file |
| `ai-agent help` | Show help |

---

**Enjoy your local AI assistant! 🤖**