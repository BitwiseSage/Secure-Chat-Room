from cryptography.fernet import Fernet

cipher = None

def generate_key():
    global cipher
    key = Fernet.generate_key()
    cipher = Fernet(key)
    print("Generated encryption key:", key)
    return key

def set_key(key):
    global cipher
    cipher = Fernet(key)

def encrypt_message(message):
    return cipher.encrypt(message.encode()).decode()

def decrypt_message(token):
    return cipher.decrypt(token.encode()).decode()