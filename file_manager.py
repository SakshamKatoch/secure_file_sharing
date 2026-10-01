from cryptography.fernet import Fernet
from pathlib import Path
import uuid


STORAGE_FOLDER = Path("storage")
KEY_FILE = Path("secret.key")


def create_key():
    if not KEY_FILE.exists():
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)


def get_cipher():
    create_key()
    key = KEY_FILE.read_bytes()
    return Fernet(key)


def encrypt_file(uploaded_file):
    cipher = get_cipher()

    file_data = uploaded_file.read()

    encrypted_data = cipher.encrypt(file_data)

    STORAGE_FOLDER.mkdir(exist_ok=True)

    stored_filename = f"{uuid.uuid4().hex}.encrypted"
    file_path = STORAGE_FOLDER / stored_filename

    file_path.write_bytes(encrypted_data)

    return stored_filename


def decrypt_file(stored_filename):
    cipher = get_cipher()

    file_path = STORAGE_FOLDER / stored_filename

    encrypted_data = file_path.read_bytes()

    return cipher.decrypt(encrypted_data)