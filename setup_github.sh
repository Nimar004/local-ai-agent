#!/bin/bash

# GitHub Setup Script for AI Agent
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${CYAN}==========================================${NC}"
    echo -e "${CYAN}   $1${NC}"
    echo -e "${CYAN}==========================================${NC}"
    echo ""
}

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

# Check prerequisites
check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    print_success "Git is installed"
}

check_gh() {
    if ! command -v gh &> /dev/null; then
        print_status "Installing GitHub CLI..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install gh
        else
            print_error "Please install GitHub CLI manually"
            exit 1
        fi
    fi
    print_success "GitHub CLI is available"
}

# Create repository
create_repo() {
    print_status "Creating GitHub repository..."
    
    if ! gh auth status &> /dev/null; then
        print_status "Please authenticate with GitHub..."
        gh auth login
    fi
    
    REPO_NAME="local-ai-agent"
    
    if gh repo view "$REPO_NAME" &> /dev/null; then
        print_status "Repository already exists"
    else
        gh repo create "$REPO_NAME" --public --description "A powerful, safe, and platform-independent local AI agent system" --add-readme --license MIT
        print_success "Repository created"
    fi
}

# Create structure
create_structure() {
    print_status "Creating repository structure..."
    mkdir -p .github/workflows .github/ISSUE_TEMPLATE docs examples
    print_success "Structure created"
}

# Create files
create_files() {
    print_status "Creating repository files..."
    
    # .gitignore
    cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
venv/
.env
.DS_Store
logs/
data/
memory/
models/
*.log
EOF

    # LICENSE
    cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

    # CONTRIBUTING.md
    cat > CONTRIBUTING.md << 'EOF'
# Contributing to Local AI Agent

Thank you for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## Code Style

- Follow PEP 8
- Use Black for formatting
- Write docstrings

## Questions?

Open an issue or contact the maintainers.
EOF

    # GitHub Actions
    cat > .github/workflows/ci.yml << 'EOF'
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - run: pip install -r requirements.txt pytest
    - run: pytest tests/ -v
EOF

    print_success "Files created"
}

# Initialize git
init_git() {
    print_status "Initializing git..."
    
    if [ ! -d ".git" ]; then
        git init
        git add .
        git commit -m "Initial commit: Local AI Agent v1.0.0"
        git branch -M main
        
        GITHUB_USER=$(gh api user --jq .login)
        git remote add origin "https://github.com/$GITHUB_USER/local-ai-agent.git"
        
        print_success "Git initialized"
    fi
}

# Push to GitHub
push_to_github() {
    print_status "Pushing to GitHub..."
    git push -u origin main
    print_success "Pushed to GitHub"
}

# Create release
create_release() {
    print_status "Creating release..."
    gh release create v1.0.0 --title "Local AI Agent v1.0.0" --notes "Initial release"
    print_success "Release created"
}

# Main
main() {
    print_header "GitHub Setup for Local AI Agent"
    
    check_git
    check_gh
    create_repo
    create_structure
    create_files
    init_git
    push_to_github
    create_release
    
    print_header "Setup Complete!"
    
    GITHUB_USER=$(gh api user --jq .login)
    echo "Repository: https://github.com/$GITHUB_USER/local-ai-agent"
    echo ""
    echo "Next steps:"
    echo "1. Star your repository"
    echo "2. Share on Reddit, Hacker News, Twitter"
    echo "3. Build your community"
    echo ""
    echo "Good luck! 🚀"
}

main