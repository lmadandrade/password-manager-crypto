from src.crypto_utils import generate_salt, derive_key, encrypt_password, decrypt_password
from src.crypto_utils import bytes_to_base64, base64_to_bytes

# Test master password
master_password = "MyMasterPassword"

# Generate salt
salt = generate_salt()

# Derive encryption key
key = derive_key(master_password, salt)

# Password we want to protect
password = "MySecretPassword123"

# Encrypt the password
nonce, ciphertext = encrypt_password(password, key)

print("Encrypted password:", ciphertext)

# Decrypt the password
decrypted = decrypt_password(ciphertext, nonce, key)

print("Decrypted password:", decrypted)

# Check if everything worked
if decrypted == password:
    print("Test successful: encryption and decryption work correctly")
else:
    print("Test failed")

# Test Base64 conversion
sample_bytes = b"test_data"

encoded = bytes_to_base64(sample_bytes)
decoded = base64_to_bytes(encoded)

print("Base64 encoded:", encoded)
print("Base64 decoded:", decoded)

if decoded == sample_bytes:
    print("Base64 test successful")
else:
    print("Base64 test failed")
