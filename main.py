import socket
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

def diffie_hellman_key_exchange(user_p, user_g, user_private_key):
    p = user_p
    g = user_g
    private_key = user_private_key
    public_key = pow(g, private_key, p)
    return p, g, private_key, public_key

def generate_shared_secret(private_key, other_public_key, p):
    return pow(other_public_key, private_key, p)

def encrypt_message(message, key):
    backend = default_backend()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    encrypted_message = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_message

def decrypt_message(encrypted_message, key):
    backend = default_backend()
    iv = encrypted_message[:16]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_padded_message = decryptor.update(encrypted_message[16:]) + decryptor.finalize()
    decrypted_message = unpadder.update(decrypted_padded_message) + unpadder.finalize()
    return decrypted_message.decode()

def derive_key(shared_secret):
    return hashlib.sha256(str(shared_secret).encode()).digest()

def start_client():
    host = input('Enter hostname or host IP: ')
    port = 8080
    p = int(input("Enter a prime number (p): "))
    g = int(input("Enter a base number (g): "))
    private_key = int(input("Enter your private key: "))
    _, _, client_private_key, client_public_key = diffie_hellman_key_exchange(p, g, private_key)
    s = socket.socket()
    s.connect((host, port))
    print('Connected to chat server')
    s.send(f"{client_public_key}".encode())
    server_public_key = int(s.recv(1024).decode())
    shared_secret = generate_shared_secret(client_private_key, server_public_key, p)
    key = derive_key(shared_secret)
    print("Shared secret established.")
    while True:
        incoming_message = s.recv(1024)
        decrypted_message = decrypt_message(incoming_message, key)
        print('Server:', decrypted_message)
        print()
        message = input('>> ')
        encrypted_message = encrypt_message(message, key)
        s.send(encrypted_message)
        print('Sent')
        print()

def start_server():
    host = socket.gethostname()
    port = 8081
    p = int(input("Enter a prime number (p): "))
    g = int(input("Enter a base number (g): "))
    private_key = int(input("Enter your private key: "))
    _, _, server_private_key, server_public_key = diffie_hellman_key_exchange(p, g, private_key)
    s = socket.socket()
    s.bind((host, port))
    print('Server will start on host:', host)
    print()
    print('Waiting for connection...')
    print()
    s.listen(1)
    conn, addr = s.accept()
    print(addr, 'has connected to the server')
    print()
    client_public_key = int(conn.recv(1024).decode())
    conn.send(f"{server_public_key}".encode())
    shared_secret = generate_shared_secret(server_private_key, client_public_key, p)
    key = derive_key(shared_secret)
    print("Shared secret established.")
    while True:
        message = input('>> ')
        encrypted_message = encrypt_message(message, key)
        conn.send(encrypted_message)
        print('Sent')
        print()
        incoming_message = conn.recv(1024)
        decrypted_message = decrypt_message(incoming_message, key)
        print('Client:', decrypted_message)
        print()

if __name__ == "__main__":
    role = input("Do you want to be the client or server? (Enter 'client' or 'server'): ").strip().lower()
    if role == 'client':
        start_client()
    elif role == 'server':
        start_server()
    else:
        print("Invalid choice. Please enter 'client' or 'server'.")
