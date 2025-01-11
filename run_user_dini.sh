#!/bin/bash

# Ensure the script exits immediately on error
set -e

echo "Starting backend background classes..."
python playground/user_backend_background.py &  # Run in the background
BACKEND_PID=$!  # Capture the backend process ID

# Step 1: Navigate to the playground directory and run the sample_background.py script
echo "Starting the backend server..."
python playground/user_backend.py &  # Run in the background
BACKEND_PID=$!  # Capture the backend process ID


# Step 2: Wait for the backend to be ready (adjust the sleep run_sample_dini.sh if needed)
echo "Waiting for the backend to initialize..."
sleep 5  # Allow run_sample_dini.sh for the backend to start

# Alternatively, check for readiness using curl or a similar tool
# until curl -s http://localhost:<backend_port>/health-check; do sleep 1; done

# Step 3: Navigate to the frontend directory and install dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install

# Step 4: Start the frontend server
echo "Starting the frontend server..."
npm run dev

# Keep the script running until the backend process exits
wait $BACKEND_PID
