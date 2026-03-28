#!/usr/bin/env bash

# Universal Local AI Agent Setup Script
# Works on macOS, Linux, and Windows (WSL/Git Bash)

set -e

# Colors (works on most terminals)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    elif [[ -f /proc/version ]] && grep -q Microsoft /proc/version; then
        echo "wsl"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)

# Print functions
print_header() {
    echo ""
    echo -e "${CYAN}==========================================${NC}"
    echo -e "${CYAN}   $1${NC}"
    echo -e "${CYAN}==========================================${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Get installation directory
get_install_dir() {
    if [ -n "$1" ]; then
        INSTALL_DIR="$1"
    else
        case $OS in
            macos)
                DEFAULT_DIR="$HOME/ai-agent"
                ;;
            linux|wsl)
                DEFAULT_DIR="$HOME/ai-agent"
                ;;
            windows)
                DEFAULT_DIR="$USERPROFILE/ai-agent"
                ;;
            *)
                DEFAULT_DIR="$HOME/ai-agent"
                ;;
        esac
        
        read -p "Installation directory [default: $DEFAULT_DIR]: " INSTALL_DIR
        INSTALL_DIR=${INSTALL_DIR:-$DEFAULT_DIR}
    fi
    
    # Expand tilde
    INSTALL_DIR="${INSTALL_DIR/#\~/$HOME}"
    
    echo "$INSTALL_DIR"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install package manager
install_package_manager() {
    print_status "Checking package manager..."
    
    case $OS in
        macos)
            if ! command_exists brew; then
                print_status "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                
                # Add to PATH for Apple Silicon
                if [[ $(uname -m) == 'arm64' ]]; then
                    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                fi
                
                print_success "Homebrew installed"
            else
                print_success "Homebrew already installed"
            fi
            ;;
            
        linux)
            if command_exists apt-get; then
                print_success "apt-get available"
            elif command_exists yum; then
                print_success "yum available"
            elif command_exists dnf; then
                print_success "dnf available"
            elif command_exists pacman; then
                print_success "pacman available"
            else
                print_warning "No recognized package manager found"
            fi
            ;;
            
        windows|wsl)
            if command_exists choco; then
                print_success "Chocolatey available"
            elif command_exists scoop; then
                print_success "Scoop available"
            else
                print_warning "No package manager found. Install Chocolatey or Scoop manually."
            fi
            ;;
    esac
}

# Install Python
install_python() {
    print_status "Checking Python..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION installed"
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        if [[ $PYTHON_VERSION == 3.* ]]; then
            print_success "Python $PYTHON_VERSION installed"
            PYTHON_CMD="python"
        else
            print_warning "Python 2 detected, installing Python 3..."
            install_python_package
        fi
    else
        print_status "Installing Python..."
        install_python_package
    fi
}

install_python_package() {
    case $OS in
        macos)
            brew install python@3.11
            PYTHON_CMD="python3"
            ;;
        linux)
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv
            elif command_exists yum; then
                sudo yum install -y python3 python3-pip
            elif command_exists dnf; then
                sudo dnf install -y python3 python3-pip
            fi
            PYTHON_CMD="python3"
            ;;
        windows|wsl)
            if command_exists choco; then
                choco install python -y
            else
                print_error "Please install Python manually from python.org"
                exit 1
            fi
            PYTHON_CMD="python"
            ;;
    esac
    
    print_success "Python installed"
}

# Install Ollama
install_ollama() {
    print_status "Checking Ollama..."
    
    if command_exists ollama; then
        print_success "Ollama already installed"
    else
        print_status "Installing Ollama..."
        
        case $OS in
            macos)
                brew install ollama
                ;;
            linux|wsl)
                curl -fsSL https://ollama.com/install.sh | sh
                ;;
            windows)
                print_warning "Please install Ollama manually from https://ollama.com"
                print_warning "After installation, restart this script"
                exit 1
                ;;
        esac
        
        print_success "Ollama installed"
    fi
}

# Start Ollama
start_ollama() {
    print_status "Starting Ollama service..."
    
    if pgrep -x "ollama" > /dev/null 2>&1; then
        print_success "Ollama is already running"
    else
        case $OS in
            macos|linux|wsl)
                nohup ollama serve > "$INSTALL_DIR/logs/ollama.log" 2>&1 &
                sleep 5
                
                if pgrep -x "ollama" > /dev/null 2>&1; then
                    print_success "Ollama service started"
                else
                    print_error "Failed to start Ollama"
                    exit 1
                fi
                ;;
            windows)
                print_warning "Please start Ollama manually"
                ;;
        esac
    fi
}

# Pull default model
pull_model() {
    print_status "Pulling default model (llama3.2)..."
    
    if ollama list 2>/dev/null | grep -q "llama3.2"; then
        print_success "Model llama3.2 already exists"
    else
        ollama pull llama3.2
        print_success "Model llama3.2 pulled"
    fi
}

# Create directory structure
create_directories() {
    print_status "Creating directory structure..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/src"
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/data"
    mkdir -p "$INSTALL_DIR/models"
    mkdir -p "$INSTALL_DIR/config"
    
    print_success "Directories created"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    $PYTHON_CMD -m venv venv
    
    # Activate virtual environment
    case $OS in
        windows)
            source venv/Scripts/activate
            ;;
        *)
            source venv/bin/activate
            ;;
    esac
    
    # Upgrade pip
    pip install --upgrade pip -q
    
    # Install dependencies
    pip install -q \
        aiohttp \
        ollama \
        beautifulsoup4 \
        selenium \
        pyautogui \
        Pillow \
        moviepy \
        opencv-python \
        chardet \
        psutil
    
    print_success "Python dependencies installed"
}

# Copy source files
copy_files() {
    print_status "Copying source files..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    # Copy source files
    if [ -d "$SCRIPT_DIR/src" ]; then
        cp -r "$SCRIPT_DIR/src/"* "$INSTALL_DIR/src/"
    fi
    
    # Copy other files
    for file in requirements.txt README.md USER_GUIDE.md ENHANCED_FEATURES.md; do
        if [ -f "$SCRIPT_DIR/$file" ]; then
            cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/"
        fi
    done
    
    print_success "Files copied"
}

# Create management script
create_management_script() {
    print_status "Creating management script..."
    
    case $OS in
        windows)
            MANAGE_SCRIPT="$INSTALL_DIR/manage.bat"
            cat > "$MANAGE_SCRIPT" << 'EOF'
@echo off
setlocal

cd /d "%~dp0"

if "%1"=="start" (
    echo Starting AI Agent (CLI mode)...
    call venv\Scripts\activate
    python src\main.py interactive
) else if "%1"=="start-web" (
    echo Starting AI Agent (Web mode)...
    call venv\Scripts\activate
    python src\main.py --mode web --port 8080
) else if "%1"=="stop" (
    echo Stopping AI Agent...
    taskkill /F /IM python.exe 2>nul
    echo Stopped
) else if "%1"=="status" (
    echo === Status ===
    tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul && echo [✓] Ollama: Running || echo [✗] Ollama: Stopped
    ollama list 2>nul
    tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" >nul && echo [✓] AI Agent: Running || echo [✗] AI Agent: Stopped
) else if "%1"=="models" (
    ollama list
) else (
    echo Local AI Agent Management
    echo.
    echo Usage: %0 [COMMAND]
    echo.
    echo Commands:
    echo   start       Start CLI mode
    echo   start-web   Start web interface
    echo   stop        Stop the agent
    echo   status      Show status
    echo   models      List models
)

endlocal
EOF
            ;;
            
        *)
            MANAGE_SCRIPT="$INSTALL_DIR/manage.sh"
            cat > "$MANAGE_SCRIPT" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

case "${1:-help}" in
    start)
        echo "Starting AI Agent (CLI mode)..."
        source venv/bin/activate
        python src/main.py interactive
        ;;
    start-web)
        echo "Starting AI Agent (Web mode)..."
        source venv/bin/activate
        python src/main.py --mode web --port 8080
        ;;
    stop)
        echo "Stopping AI Agent..."
        pkill -f "python src/main.py" 2>/dev/null || true
        echo "Stopped"
        ;;
    status)
        echo "=== Status ==="
        if pgrep -x "ollama" > /dev/null 2>&1; then
            echo "✓ Ollama: Running"
            ollama list 2>/dev/null || echo "  Could not list models"
        else
            echo "✗ Ollama: Stopped"
        fi
        if pgrep -f "python src/main.py" > /dev/null 2>&1; then
            echo "✓ AI Agent: Running"
        else
            echo "✗ AI Agent: Stopped"
        fi
        ;;
    models)
        ollama list
        ;;
    help|*)
        echo "Local AI Agent Management"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  start       Start CLI mode"
        echo "  start-web   Start web interface (port 8080)"
        echo "  stop        Stop the agent"
        echo "  status      Show status"
        echo "  models      List models"
        echo "  help        Show this help"
        ;;
esac
EOF
            chmod +x "$MANAGE_SCRIPT"
            ;;
    esac
    
    print_success "Management script created"
}

# Create desktop shortcut
create_shortcut() {
    print_status "Creating desktop shortcut..."
    
    case $OS in
        macos)
            cat > "$HOME/Desktop/AI Agent.command" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
./manage.sh status
echo ""
read -p "Press Enter to exit..."
EOF
            chmod +x "$HOME/Desktop/AI Agent.command"
            ;;
            
        linux)
            cat > "$HOME/Desktop/ai-agent.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AI Agent
Comment=Local AI Assistant
Exec=$INSTALL_DIR/manage.sh status
Icon=utilities-terminal
Terminal=true
Categories=Utility;
EOF
            chmod +x "$HOME/Desktop/ai-agent.desktop"
            ;;
            
        windows)
            echo "Creating Windows shortcut..."
            # Create a batch file on desktop
            cat > "$USERPROFILE/Desktop/AI Agent.bat" << EOF
@echo off
cd /d "$INSTALL_DIR"
manage.bat status
pause
EOF
            ;;
    esac
    
    print_success "Desktop shortcut created"
}

# Create shell alias
create_alias() {
    print_status "Creating shell alias..."
    
    case $OS in
        macos|linux|wsl)
            if [[ $SHELL == *"zsh"* ]]; then
                SHELL_RC="$HOME/.zshrc"
            elif [[ $SHELL == *"bash"* ]]; then
                SHELL_RC="$HOME/.bashrc"
            else
                SHELL_RC="$HOME/.profile"
            fi
            
            if ! grep -q "alias ai-agent=" "$SHELL_RC" 2>/dev/null; then
                echo "" >> "$SHELL_RC"
                echo "# Local AI Agent" >> "$SHELL_RC"
                echo "alias ai-agent='$INSTALL_DIR/manage.sh'" >> "$SHELL_RC"
                print_success "Alias 'ai-agent' created"
                print_status "Run 'source $SHELL_RC' or restart your terminal"
            else
                print_success "Alias already exists"
            fi
            ;;
            
        windows)
            print_warning "Alias not supported on Windows. Use manage.bat directly."
            ;;
    esac
}

# Show final instructions
show_instructions() {
    print_header "Setup Complete!"
    
    echo "Installation directory: $INSTALL_DIR"
    echo ""
    echo "Quick Start:"
    
    case $OS in
        windows)
            echo "  cd $INSTALL_DIR"
            echo "  manage.bat start        # CLI mode"
            echo "  manage.bat start-web    # Web mode"
            echo "  manage.bat status       # Check status"
            echo "  manage.bat stop         # Stop"
            ;;
        *)
            echo "  cd $INSTALL_DIR"
            echo "  ./manage.sh start        # CLI mode"
            echo "  ./manage.sh start-web    # Web mode (http://localhost:8080)"
            echo "  ./manage.sh status       # Check status"
            echo "  ./manage.sh stop         # Stop"
            echo ""
            echo "Or use alias: ai-agent [command]"
            ;;
    esac
    
    echo ""
    echo "Web interface: http://localhost:8080"
    echo ""
    echo "Documentation: $INSTALL_DIR/USER_GUIDE.md"
    echo ""
    echo "=========================================="
}

# Main installation
main() {
    print_header "Local AI Agent - Universal Setup"
    
    echo "Detected OS: $OS"
    echo ""
    
    # Get installation directory
    INSTALL_DIR=$(get_install_dir "$1")
    
    echo ""
    print_status "Installing to: $INSTALL_DIR"
    echo ""
    
    # Confirm
    read -p "Continue with installation? (Y/n): " confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        print_status "Installation cancelled"
        exit 0
    fi
    
    echo ""
    
    # Run installation
    install_package_manager
    install_python
    install_ollama
    create_directories
    start_ollama
    pull_model
    install_dependencies
    copy_files
    create_management_script
    create_shortcut
    create_alias
    
    # Show instructions
    show_instructions
}

# Run main
main "$@"