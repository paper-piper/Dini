


## ✅ `setup.sh`

#!/bin/bash

echo "🔧 Setting up Python backend..."

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run key generation script
echo "🔑 Generating keys..."
python utils/keys_manager.py

# Frontend setup
echo "📦 Installing frontend dependencies..."
cd frontend || exit
npm install

# Add shadcn component
echo "✨ Adding ShadCN select component..."
npx shadcn add select

echo "✅ Setup complete!"
