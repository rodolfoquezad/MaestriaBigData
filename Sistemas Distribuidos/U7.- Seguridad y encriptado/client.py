import socket
import threading
import rsa
import json
from getpass import getpass

host = "127.0.0.1"
port = 1001

username = input("Ingresa tu nombre de usuario:")
password = getpass("Ingresa tu contraseña:")

creds = {}

public_key, private_key = rsa.newkeys(1024)
public_key_partner = None

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
print(f"Conectado al servidor en {host}: {port}")

client.send(public_key.save_pkcs1("PEM"))

def authenticate_users(client):
    creds = {
        "username": username,
        "password": password
    }
    creds = json.dumps(creds)
    client.send(creds.encode())
    response = client.recv(1024).decode()
    if response == "Autenticado":
        print("Autenticado")
        return True
    else:
        return False        

def get_public_key(client):
    global public_key_partner
    client.send("CMD: public_key".encode())
    try:
        data = client.recv(1024)
        if data.startswith(b"-----BEGIN RSA PUBLIC KEY-----"):
            public_key_partner = rsa.PublicKey.load_pkcs1(data)
        else:
            print("Error: No se recibió una clave pública válida.")
    except Exception as e:
        print(f"Error al recibir la clave pública: {e}")

def send_message(client):
    global public_key_partner
    while True:
        try:
            message = input()
            if message:
                if public_key_partner is None:
                    get_public_key(client)
                message = rsa.encrypt(message.encode(), public_key_partner)
                client.send(message)
                print(f"{username}: {message}")
        except Exception as e:
            print(f"Error al enviar el mensaje: {e}")

def receive_message(client):
    global public_key_partner
    while True:
        try:
            encrypted_message = client.recv(1024)
            if encrypted_message:
                if public_key_partner is None:
                    get_public_key(client)
                message = rsa.decrypt(encrypted_message, private_key).decode()
                print(f"Recibido: {message}")
        except rsa.pkcs1.DecryptionError:
            print("Error al descifrar el mensaje")

if __name__ == "__main__":
    auth = authenticate_users(client)
    if auth:
        threading.Thread(target=send_message, args=(client,)).start()
        threading.Thread(target=receive_message, args=(client,)).start()
    else:
        print("Error de autenticacion")
        client.close()