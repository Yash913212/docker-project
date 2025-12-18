#!/bin/bash
set -e

# Ensure directories exist
mkdir -p /data /cron

# Start cron daemon
echo "Starting cron daemon..."
service cron start

# Wait a moment for cron to initialize
sleep 2

# Start the FastAPI application in the foreground
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8080
