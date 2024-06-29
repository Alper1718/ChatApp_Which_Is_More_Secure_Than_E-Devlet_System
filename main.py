import socket
import hashlib
import threading
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
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
    encrypted_message = encryptor.update(message.encode()) + encryptor.finalize()
    return iv + encrypted_message

def decrypt_message(encrypted_message, key):
    backend = default_backend()
    iv = encrypted_message[:16]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message[16:]) + decryptor.finalize()
    return decrypted_message.decode()

def derive_key(shared_secret):
    return hashlib.sha256(str(shared_secret).encode()).digest()

def handle_receive(socket, key):
    while True:
        try:
            incoming_message = socket.recv(1024)
            if incoming_message:
                decrypted_message = decrypt_message(incoming_message, key)
                print('Received:', decrypted_message)
            else:
                break
        except Exception as e:
            print(f"Error in receiving message: {e}")
            break

def handle_send(socket, key):
    while True:
        try:
            message = input('>> ')
            encrypted_message = encrypt_message(message, key)
            socket.send(encrypted_message)
            print('Sent')
        except Exception as e:
            print(f"Error in sending message: {e}")
            break

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
    
    receive_thread = threading.Thread(target=handle_receive, args=(s, key))
    send_thread = threading.Thread(target=handle_send, args=(s, key))
    
    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()
    s.close()

def start_server():
    host = socket.gethostname()
    port = 8080
    p = int(input("Enter a prime number (p): "))
    g = int(input("Enter a base number (g): "))
    private_key = int(input("Enter your private key: "))
    _, _, server_private_key, server_public_key = diffie_hellman_key_exchange(p, g, private_key)
    s = socket.socket()
    s.bind((host, port))
    print('Server will start on host:', host)
    print('Waiting for connection...')
    s.listen(1)
    conn, addr = s.accept()
    print(addr, 'has connected to the server')
    client_public_key = int(conn.recv(1024).decode())
    conn.send(f"{server_public_key}".encode())
    shared_secret = generate_shared_secret(server_private_key, client_public_key, p)
    key = derive_key(shared_secret)
    print("Shared secret established.")
    
    receive_thread = threading.Thread(target=handle_receive, args=(conn, key))
    send_thread = threading.Thread(target=handle_send, args=(conn, key))
    
    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()
    conn.close()
    s.close()

if __name__ == "__main__":
    role = input("Do you want to be the client or server? (Enter 'client' or 'server'): ").strip().lower()
    if role == 'client':
        start_client()
    elif role == 'server':
        start_server()
    else:
        print("Invalid choice. Please enter 'client' or 'server'.")