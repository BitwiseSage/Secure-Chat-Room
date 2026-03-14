from cryptography.fernet import Fernet

key=Fernet.generate_key()

cipher=Fernet(key)

def encrypt_message(message):

    return cipher.encrypt(message.encode()).decode()

def decrypt_message(message):

    return cipher.decrypt(message.encode()).decode()

def generate_key():

    return key