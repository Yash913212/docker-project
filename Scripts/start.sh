#!/bin/sh
set -e

# Ensure directories exist
mkdir -p /data /cron

# Start cron daemon (Debian: 'cron')
echo "Starting cron daemon..."
if command -v cron >/dev/null 2>&1; then
	cron
else
	# Fallback to /usr/sbin/cron if PATH not set
	/usr/sbin/cron
fi

# Reduced sleep for faster startup
sleep 1

# Start the FastAPI application in the foreground
echo "Starting FastAPI application..."
exec python -m uvicorn main:app --host 0.0.0.0 --port 8080
