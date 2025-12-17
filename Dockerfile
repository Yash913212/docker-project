# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build-time dependencies if any (e.g., for compiling packages)
# RUN apt-get update && apt-get install -y build-essential

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim

# Set timezone to UTC
ENV TZ=UTC
WORKDIR /app

# Install runtime dependencies (cron)
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Copy dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY main.py .
COPY scripts/ /app/scripts/

# Copy keys required for the application to run
COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .

# Set up cron job
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

# Create mount points for persistent data
RUN mkdir -p /data /cron
VOLUME ["/data", "/cron"]

EXPOSE 8080

# Use a startup script to run both services
COPY scripts/start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
