#!/bin/bash

# Ol-GUI Setup Script
# Automates the installation and setup process

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the absolute path to the repository root
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}=== Ol-GUI Setup ===${NC}\n"

# Check Python version
echo -e "${BLUE}[1/5]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python 3.10+ is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}\n"

# Check if tkinter is available
echo -e "${BLUE}[2/5]${NC} Checking for tkinter..."
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo -e "${YELLOW}Warning: tkinter not found${NC}"
    echo "Please install it with: sudo apt install python3-tk"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ tkinter is available${NC}\n"
fi

# Install Python dependencies
echo -e "${BLUE}[3/5]${NC} Installing Python dependencies..."
cd "$REPO_DIR"

if [ -f "requirements.txt" ]; then
    # Check if user wants to use a virtual environment
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        read -p "Create a virtual environment? (recommended) (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 -m venv venv
            source venv/bin/activate
            echo -e "${GREEN}✓ Virtual environment created and activated${NC}"
        fi
    else
        # Activate existing virtual environment
        if [ -d "venv" ]; then
            source venv/bin/activate
            echo -e "${GREEN}✓ Activated existing virtual environment${NC}"
        elif [ -d ".venv" ]; then
            source .venv/bin/activate
            echo -e "${GREEN}✓ Activated existing virtual environment${NC}"
        fi
    fi

    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}\n"
else
    echo -e "${RED}Error: requirements.txt not found${NC}"
    exit 1
fi

# Update .desktop file paths
echo -e "${BLUE}[4/5]${NC} Configuring desktop entry..."
DESKTOP_FILE="$REPO_DIR/ol-gui.desktop"

if [ -f "$DESKTOP_FILE" ]; then
    # Create a temporary file with updated paths
    sed -e "s|Exec=\$HOME.*|Exec=$REPO_DIR/run.sh|g" \
        -e "s|Icon=\$HOME.*|Icon=$REPO_DIR/assets/icon.png|g" \
        "$DESKTOP_FILE" > "$DESKTOP_FILE.tmp"

    mv "$DESKTOP_FILE.tmp" "$DESKTOP_FILE"
    echo -e "${GREEN}✓ Desktop entry configured with paths:${NC}"
    echo "  Exec: $REPO_DIR/run.sh"
    echo "  Icon: $REPO_DIR/assets/icon.png"
else
    echo -e "${RED}Error: ol-gui.desktop not found${NC}"
    exit 1
fi

# Copy desktop file to local applications
echo -e "\n${BLUE}[5/5]${NC} Installing desktop entry..."
DESKTOP_DIR="$HOME/.local/share/applications"

if [ ! -d "$DESKTOP_DIR" ]; then
    mkdir -p "$DESKTOP_DIR"
    echo -e "${GREEN}✓ Created $DESKTOP_DIR${NC}"
fi

cp "$DESKTOP_FILE" "$DESKTOP_DIR/"
echo -e "${GREEN}✓ Desktop entry installed to $DESKTOP_DIR${NC}\n"

# Make run.sh executable
chmod +x "$REPO_DIR/run.sh"

# Check if Ollama is installed
echo -e "${BLUE}Checking for Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is installed${NC}"

    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${GREEN}✓ Ollama is running${NC}"
    else
        echo -e "${YELLOW}⚠ Ollama is not running${NC}"
        echo "Start it with: ollama serve"
    fi
else
    echo -e "${YELLOW}⚠ Ollama is not installed${NC}"
    echo "Install it from: https://ollama.ai"
fi

echo -e "\n${GREEN}=== Setup Complete! ===${NC}\n"
echo "To run Ol-GUI:"
echo "  1. From command line: ./run.sh"
echo "  2. From applications menu: Search for 'OL-GUI'"
echo ""
echo "Configuration files:"
echo "  - Settings: ~/.config/ol-gui/settings.json"
echo "  - Database: ~/.local/share/ol-gui/conversations.db"
echo ""
echo -e "${BLUE}Enjoy using Ol-GUI!${NC}"
