###########################################
# Stage 1: Builder
###########################################
FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


###########################################
# Stage 2: Runtime
###########################################
FROM python:3.10-slim

ENV TZ=UTC
WORKDIR /app

# Install cron + tzdata
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Configure timezone
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Copy installed Python packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Copy the PEM key file into the container
COPY student_public.pem /app/student_public.pem

# Copy cron job file into /cron path
RUN mkdir -p /cron && \
    cp cron/2fa-cron /cron/2fa-cron && \
    chmod 0644 /cron/2fa-cron && \
    crontab /cron/2fa-cron

# Prepare mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

VOLUME ["/data", "/cron"]

EXPOSE 8080

CMD service cron start && uvicorn main:app --host 0.0.0.0 --port 8080
