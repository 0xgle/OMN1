from cryptography.fernet import Fernet

# Replace this key with your real one or load from file
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_file(input_file, output_file):
    with open(input_file, "rb") as f:
        data = f.read()
    encrypted = cipher.encrypt(data)
    with open(output_file, "wb") as f:
        f.write(encrypted)
    print(f"[+] Encrypted report saved as {output_file}")
