#!/bin/sh

# Start the cron daemon in the background
cron

# Start the FastAPI application in the foreground
# Use --host 0.0.0.0 to make it accessible from outside the container
uvicorn main:app --host 0.0.0.0 --port 8080
