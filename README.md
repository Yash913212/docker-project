# PKI-Based 2FA TOTP Microservice

A secure, Docker-based microservice implementing Time-based One-Time Password (TOTP) authentication using RSA public key infrastructure for seed encryption and distribution.

## Features

- **RSA/OAEP Encryption**: Secure seed decryption using 4096-bit RSA keys
- **TOTP Code Generation**: RFC 6238 compliant time-based codes
- **RESTful API**: Three endpoints for decrypt, generate, and verify operations
- **Automated Cron Job**: Every-minute TOTP code logging
- **Docker Containerization**: Complete environment with persistence
- **Seed Persistence**: Docker volumes ensure seed survives container restarts

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git installed

### Running the Service

```bash
# Clone the repository
git clone <your-repo-url>
cd docker-project

# Build and start the container
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```

The API will be available at `http://localhost:8080`

## API Endpoints

### 1. POST /decrypt-seed
Decrypts the RSA-encrypted seed and stores it persistently.

**Request:**
```json
{
  "encrypted_seed": "base64-encoded-encrypted-seed"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d '{"encrypted_seed": "your-base64-encrypted-seed"}'
```

### 2. GET /generate-2fa
Generates a current TOTP code from the stored seed.

**Response:**
```json
{
  "code": "123456",
  "valid_for": 25
}
```

**Example:**
```bash
curl http://localhost:8080/generate-2fa
```

### 3. POST /verify-2fa
Verifies a TOTP code with ±1 period tolerance (90 seconds total validity).

**Request:**
```json
{
  "code": "123456"
}
```

**Response:**
```json
{
  "valid": true
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "123456"}'
```

## Project Structure

```
.
├── main.py                    # FastAPI application
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Docker Compose configuration
├── requirements.txt           # Python dependencies
├── Scripts/
│   ├── start.sh              # Container startup script
│   └── log_2fa_cron.py       # Cron job script for TOTP logging
├── cron/
│   └── 2fa-cron              # Crontab configuration
├── student_private.pem        # Student's RSA private key
├── student_public.pem         # Student's RSA public key
├── instructor_public.pem      # Instructor's RSA public key
├── encrypted_seed.txt         # Encrypted TOTP seed
├── generate_commit_proof.py   # Generates cryptographic commit proof
├── generate_student_keys.py   # Generates RSA key pairs
├── generate_totp.py           # Standalone TOTP generator
├── request_seed.py            # Requests encrypted seed from instructor
└── decrypt_seed.py            # Standalone seed decryption utility
```

## Architecture

### Cryptographic Flow
1. **Key Generation**: Student generates 4096-bit RSA key pair
2. **Seed Request**: Public key sent to instructor API
3. **Seed Encryption**: Instructor encrypts 256-bit seed with student's public key using RSA/OAEP
4. **Seed Decryption**: Student decrypts with private key
5. **TOTP Generation**: Seed converted to Base32, used with HMAC-SHA1 for 6-digit codes

### Docker Architecture
- **Multi-stage Build**: Separate builder and runtime stages for minimal image size
- **Persistent Volumes**:
  - `/data` - Stores decrypted seed
  - `/cron` - Stores cron job output
- **Cron Daemon**: Runs alongside FastAPI server
- **Uvicorn Server**: ASGI server on port 8080

## Security Considerations

- Private keys never transmitted
- RSA/OAEP with SHA-256 for hybrid encryption
- TOTP with SHA-1 (RFC 6238 standard)
- 30-second time steps with ±1 period tolerance
- Seed persistence in Docker volume (not in image)

## Development & Testing

### Run Tests
```bash
python test_api.py
```

### Manual Testing
```bash
# Decrypt seed
python decrypt_seed.py

# Generate TOTP code
python generate_totp.py

# Generate commit proof
python generate_commit_proof.py
```

### Docker Commands
```bash
# Rebuild without cache
docker-compose build --no-cache

# View container logs
docker-compose logs

# Execute command in container
docker exec totp-api <command>

# Check cron output
docker exec totp-api cat /cron/last_code.txt

# Stop and remove everything
docker-compose down -v
```

## Cron Job

The cron job runs every minute and logs TOTP codes to `/cron/last_code.txt`:

```
2025-12-18 15:02:01 - 2FA Code: 175742
2025-12-18 15:03:01 - 2FA Code: 892341
2025-12-18 15:04:01 - 2FA Code: 456789
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs
docker-compose down -v
docker-compose up --build
```

### API returns 500 errors
Check if seed is decrypted:
```bash
docker exec totp-api ls -l /data/
```

### Cron not running
Check cron status:
```bash
docker exec totp-api ps aux | grep cron
docker exec totp-api crontab -l
```

### Seed doesn't persist
Ensure volumes are properly mounted:
```bash
docker volume ls
docker-compose down -v  # removes volumes
docker-compose up -d    # recreates volumes
```

## Requirements

- Python 3.11+
- Docker 20.10+
- Docker Compose 2.0+

### Python Dependencies
- fastapi
- uvicorn
- pydantic
- cryptography
- pyotp

## License

This is a student project for educational purposes.

## Author

Student ID: [Your ID]
Course: Applied Cryptography
Assignment: PKI-Based 2FA Microservice
