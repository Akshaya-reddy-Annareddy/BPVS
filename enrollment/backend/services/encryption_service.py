from cryptography.fernet import Fernet
import json

key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_embedding(embedding):
    data = json.dumps(embedding.tolist()).encode()
    return cipher.encrypt(data)
