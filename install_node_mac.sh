#!/bin/bash

echo "🔍 Checking for Homebrew..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is not installed."
    echo ""
    echo "📋 To install Homebrew, run this command:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo ""
    echo "After installing Homebrew, run this script again."
    exit 1
fi

echo "✅ Homebrew found: $(brew --version | head -n 1)"

# Check if Node.js is already installed
if command -v node &> /dev/null; then
    echo "⚠️  Node.js is already installed:"
    echo "   Node version: $(node -v)"
    echo "   NPM version: $(npm -v)"
    echo "   Location: $(which node)"
    echo ""
    read -p "Do you want to reinstall Node.js? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping Node.js installation."
        exit 0
    fi
fi

echo "📦 Installing Node.js (LTS) via Homebrew..."
brew install node

echo ""
echo "✅ Installation complete!"
echo "   Node version: $(node -v)"
echo "   NPM version: $(npm -v)"
echo "   Location: $(which node)"

# Create .env.local for web-app if it doesn't exist
WEB_APP_DIR="$(dirname "$0")/web-app"
ENV_FILE="$WEB_APP_DIR/.env.local"

if [ ! -f "$ENV_FILE" ]; then
    echo ""
    echo "📝 Creating .env.local file for web app..."
    cat > "$ENV_FILE" << 'EOF'
# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
EOF
    echo "✅ Created $ENV_FILE"
    echo "   Please update it with your actual Firebase credentials."
else
    echo ""
    echo "ℹ️  .env.local already exists at $ENV_FILE"
fi

echo ""
echo "🎉 Setup complete! You can now run:"
echo "   cd web-app"
echo "   npm install"
echo "   npm run dev"
