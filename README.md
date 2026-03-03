## Project Overview:

This project is a simple desktop Password Manager built in Python using Tkinter for the graphical interface. It demonstrates the practical use of cryptographic concepts learned in the Security Fundamentals and Development module.

The application allows users to store login credentials (service name, username, and password) securely in a local JSON file. Instead of storing passwords in plain text, all sensitive data is encrypted before being saved.

## The system uses:

- PBKDF2 with SHA-256 to derive a secure encryption key from a master password.

- AES (Advanced Encryption Standard) to encrypt and decrypt stored passwords.

The goal of this project is to apply cryptography concepts such as confidentiality and integrity in a practical, working application.

This is a learning-focused implementation and is not intended for production use.


## Development Plan

- [x] Project structure created
- [ ] Implement key derivation (PBKDF2)
- [ ] Implement AES encryption/decryption
- [ ] Implement vault loading and saving
- [ ] Build Tkinter GUI layout
- [ ] Connect GUI to encryption logic
- [ ] Add basic validation and error handling