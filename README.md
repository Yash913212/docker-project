# PKI-Based 2FA TOTP Microservice

A simple and secure 2-Factor Authentication (2FA) microservice built using FastAPI, Docker, and basic cryptography concepts. This project uses RSA public-key encryption to safely handle a secret seed and Time-based One-Time Passwords (TOTP) to generate and verify authentication codes.

This document is written in a clear, human style and is suitable for academic submission, interviews, and GitHub portfolios.

---

## Project Overview

This microservice demonstrates how a real-world authentication system works by combining encryption, containers, and time-based security.

The service:

* Receives an encrypted secret seed
* Decrypts and stores the seed securely
* Generates 6-digit TOTP codes every 30 seconds
* Verifies user-provided TOTP codes
* Runs fully inside Docker
* Logs TOTP codes automatically using a cron job

---

## Technologies Used

* FastAPI – REST API framework
* Python – Programming language
* RSA (4096-bit) – Public key encryption
* TOTP (RFC 6238) – Time-based OTP standard
* Docker and Docker Compose – Containerization
* Cron – Automated background task

---

## How to Run the Project

### Prerequisites

* Docker installed
* Docker Compose installed
* Git installed

---

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

The API will be available at:
[http://localhost:8080](http://localhost:8080)

---

## API Endpoints

### 1. Decrypt Seed

POST /decrypt-seed

This endpoint receives an RSA-encrypted seed, decrypts it using the private key, and stores it persistently.

Request:

```json
{
  "encrypted_seed": "base64-encrypted-seed"
}
```

Response:

```json
{
  "status": "ok"
}
```

---

### 2. Generate TOTP Code

GET /generate-2fa

Generates the current 6-digit TOTP code using the stored seed.

Response:

```json
{
  "code": "123456",
  "valid_for": 25
}
```

---

### 3. Verify TOTP Code

POST /verify-2fa

Verifies whether the provided TOTP code is valid. The service allows one time window before and after the current window, giving a total tolerance of 90 seconds.

Request:

```json
{
  "code": "123456"
}
```

Response:

```json
{
  "valid": true
}
```

---

## Project Structure

```
.
├── main.py                 # FastAPI application
├── Dockerfile              # Docker build configuration
├── docker-compose.yml      # Docker Compose setup
├── requirements.txt        # Python dependencies
├── Scripts/                # Startup and cron scripts
├── cron/                   # Cron configuration
├── *.pem                   # RSA public and private keys
├── encrypted_seed.txt      # Encrypted seed
├── decrypt_seed.py         # Seed decryption utility
├── generate_totp.py        # TOTP generator
```

---

## System Workflow

1. The student generates an RSA public and private key pair.
2. The public key is shared with the instructor.
3. The instructor encrypts a secret seed using the public key.
4. The encrypted seed is sent to the microservice.
5. The service decrypts the seed using the private key.
6. The decrypted seed is stored securely in a Docker volume.
7. TOTP codes are generated every 30 seconds.
8. A cron job logs the generated codes every minute.

---

## Docker and Persistence

* FastAPI runs on port 8080.
* Cron runs inside the same container.
* Docker volumes are used to store:

  * The decrypted seed
  * Cron output logs

This ensures the data is preserved even if the container is restarted.

---

## Security Design

* Private RSA keys are never transmitted.
* The seed is always encrypted during transfer.
* RSA/OAEP with SHA-256 is used for encryption.
* TOTP follows the RFC 6238 standard.
* The seed is stored in a Docker volume, not inside the image.

---

## Testing and Debugging

Manual testing:

```bash
python decrypt_seed.py
python generate_totp.py
```

Docker commands:

```bash
# Rebuild images
docker-compose build --no-cache

# View logs
docker-compose logs

# Check cron output
docker exec totp-api cat /cron/last_code.txt

# Stop and clean up
docker-compose down -v
```

---

## Cron Job Output Example

```
2025-12-18 15:02 - 2FA Code: 175742
2025-12-18 15:03 - 2FA Code: 892341
2025-12-18 15:04 - 2FA Code: 456789
```

---

## Learning Outcomes

From this project, you learn:

* How public key infrastructure works
* How encrypted seed distribution is handled securely
* How TOTP-based authentication systems function
* How to run background tasks inside Docker
* How FastAPI services are containerized

---

## Project Information

Course: Applied Cryptography
Project Type: Student Assignment
Purpose: Educational and learning use only

---

This project demonstrates how modern authentication systems combine encryption, containers, and time-based security in a practical and understandable way.
