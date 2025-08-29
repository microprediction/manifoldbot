#!/bin/bash

# ManifoldBot Installation Script
echo "🚀 Installing ManifoldBot..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Install the package in development mode
echo "📦 Installing ManifoldBot package..."
pip3 install -e .

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Please create one with your API keys:"
    echo "   OPENAI_API_KEY=your_openai_key"
    echo "   MANIFOLD_API_KEY=your_manifold_key"
else
    echo "✅ .env file found"
fi

echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Make sure your .env file has the required API keys"
echo "2. Create a config: manifoldbot init --output my_bot.yaml"
echo "3. Run your bot: manifoldbot start --config my_bot.yaml"
echo ""
echo "For more information, see PLAN.md"
