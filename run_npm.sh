#!/bin/bash

# Helper script to run npm/node commands when they're not in PATH
# This assumes node is installed somewhere on your system

echo "🔍 Searching for node installation..."

# Common locations to check
POSSIBLE_PATHS=(
    "/usr/local/bin/node"
    "/opt/homebrew/bin/node"
    "$HOME/.nvm/versions/node/*/bin/node"
    "/Users/tinshuichan/Library/Mobile Documents/com~apple~CloudDocs/Antigravity/web-app/node_modules/.bin"
)

NODE_PATH=""

# Search for node
for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -f "$path" ] || ls $path 2>/dev/null | grep -q node; then
        NODE_PATH=$(ls $path 2>/dev/null | head -1)
        break
    fi
done

# If not found in common locations, search the system
if [ -z "$NODE_PATH" ]; then
    echo "Searching system for node..."
    NODE_PATH=$(find /usr/local /opt /Users/$USER -name "node" -type f 2>/dev/null | grep -E "bin/node$" | head -1)
fi

if [ -z "$NODE_PATH" ]; then
    echo "❌ Could not find node installation"
    echo "Please install Node.js using:"
    echo "  ./install_node_mac.sh"
    exit 1
fi

echo "✅ Found node at: $NODE_PATH"

# Get the bin directory
BIN_DIR=$(dirname "$NODE_PATH")
NPM_PATH="$BIN_DIR/npm"

if [ ! -f "$NPM_PATH" ]; then
    echo "❌ npm not found at $NPM_PATH"
    exit 1
fi

echo "✅ Found npm at: $NPM_PATH"
echo ""

# Export to PATH for this session
export PATH="$BIN_DIR:$PATH"

echo "📦 Running: npm $@"
echo ""

"$NPM_PATH" "$@"
