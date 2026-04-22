#!/bin/bash

# AI Tax Buddy - Installation Script
# This script sets up the taxbuddy and aitax commands globally

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SHELL_CONFIG=""

echo "🇦🇺 AI Tax Buddy - Installation"
echo "================================"
echo ""

# Detect shell configuration file
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    echo "⚠️  Could not detect shell. Please add manually to your shell config:"
    echo "   export PATH=\"$PROJECT_DIR/bin:\$PATH\""
    exit 1
fi

echo "Detected shell: $SHELL_NAME"
echo "Config file: $SHELL_CONFIG"
echo ""

# Check if already installed
if grep -q "$PROJECT_DIR/bin" "$SHELL_CONFIG" 2>/dev/null; then
    echo "✅ AI Tax Buddy is already in your PATH"
    echo ""
    echo "Commands available:"
    echo "  • taxbuddy"
    echo "  • aitax"
    echo ""
    exit 0
fi

# Add to PATH
echo "Adding AI Tax Buddy to PATH..."
echo "" >> "$SHELL_CONFIG"
echo "# AI Tax Buddy commands" >> "$SHELL_CONFIG"
echo "export PATH=\"$PROJECT_DIR/bin:\$PATH\"" >> "$SHELL_CONFIG"

echo "✅ Installation complete!"
echo ""
echo "To activate in current terminal:"
echo "  source $SHELL_CONFIG"
echo ""
echo "Or open a new terminal and use:"
echo "  taxbuddy chat"
echo "  aitax info"
echo ""
echo "🎉 Ready to go!"
