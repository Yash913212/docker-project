import json
import requests

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def request_seed(student_id: str, github_repo_url: str):
    # Step 1: Read the student public key AS-IS
    with open("student_public.pem", "r") as f:
        public_key_pem = f.read()

    # Step 2: Prepare payload WITHOUT modifying the key
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem   # KEEP NEWLINES
    }

    # Step 3: Send POST request
    response = requests.post(
        API_URL,
        json=payload,
        timeout=10
    )

    # Step 4: Parse response
    if response.status_code != 200:
        print("Error contacting API:", response.text)
        return

    data = response.json()

    if data.get("status") != "success":
        print("API Error:", data)
        return

    encrypted_seed = data["encrypted_seed"]

    # Step 5: Save encrypted seed
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("Encrypted seed received and saved to encrypted_seed.txt")


# -------- RUN --------
if __name__ == "__main__":
    student_id = "23P31A05D6"   # your ID
    github_repo = "https://github.com/Yash913212/docker-project"

    request_seed(student_id, github_repo)
