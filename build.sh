#!/bin/bash

# Clinic Scout - Production Build Script
# This script ensures you're in the correct directory before building

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $(pwd)"
echo ""

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in current directory"
    echo "Please run this script from the Antigravity root directory"
    exit 1
fi

echo "✅ Found package.json"
echo ""

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    ./run_npm.sh install
    echo ""
fi

# Run build
echo "🏗️  Building production bundle..."
./run_npm.sh run build

echo ""
echo "✅ Build complete!"
echo ""
echo "To test locally, run:"
echo "  ./run_npm.sh start"
echo ""
echo "To deploy to Vercel:"
echo "  git add ."
echo "  git commit -m 'Production build'"
echo "  git push origin main"
