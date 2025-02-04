#!/bin/bash

# Ensure the script exits immediately on error
set -e

echo "Starting backend background classes..."
python backend/dini_support_system.py &  # Run in the background
BACKEND_PID=$!  # Capture the backend process ID

# Step 1: Navigate to the playground directory and run the sample_background.py script
echo "Starting the backend server..."
python backend//user_backend.py &  # Run in the background
BACKEND_PID=$!  # Capture the backend process ID

# Step 2: Wait for the backend to be ready (adjust the sleep run_sample_dini.sh if needed)
echo "Waiting for the backend to initialize..."
sleep 1  # Allow run_sample_dini.sh for the backend to start

# Step 4: Start the frontend server
echo "Starting the frontend server..."
cd frontend
npm run dev

# Keep the script running until the backend process exits
wait $BACKEND_PID
