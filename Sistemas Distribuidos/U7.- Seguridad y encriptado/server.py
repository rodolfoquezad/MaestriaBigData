import socket
import threading
import rsa
import json

host = "127.0.0.1"
port = 1001

clients = {}
passwords = {"Rodolfo": "admin", "Alfredo": "admin"}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print(f"Servidor en espera de conexiones en {host}: {port}")

def handle_client(client, addr):
    try:
        auth = authenticate_user(client, addr)
        if auth:
            auth_response = "Autenticado"
            client.send(auth_response.encode())
            while True:
                try:
                    message = client.recv(1024)
                    if message:
                        if message.startswith(b"CMD:"):
                            send_public_key(client, addr)
                        else:
                            print(f"Mensaje recibido de {addr}: {message}")
                            broadcast(message, addr)
                    else:
                        break
                except Exception as e:
                    print(f"Error recibiendo mensaje de {addr}: {e}")
                    break
    except Exception as e:
        print(f"Error manejando el cliente {addr}: {e}")
    finally:
        client.close()
        remove_client(addr)

def authenticate_user(client, addr):
    try:
        public_key_partner = rsa.PublicKey.load_pkcs1(client.recv(1024))
        creds = client.recv(1024).decode()
        creds = json.loads(creds)
        if creds['username'] in passwords and passwords[creds['username']] == creds['password']:
            clients[creds['username']] = {
                "socket": client,
                "public_key_partner": public_key_partner, 
                "address": addr
            }
            print(f"{creds['username']} se ha conectado desde {addr}")
            return True
        else:
            return False
    except Exception as e:
        print(f"Error autenticando el cliente {addr}: {e}")
        return False

def send_public_key(client, addr):
    try:
        for client_info in clients.values():
            if client_info["address"] != addr:
                public_key = client_info["public_key_partner"]
                client.send(public_key.save_pkcs1("PEM"))
    except Exception as e:
        print(f"Error enviando llave publica a {addr}: {e}")

def broadcast(message, addr):
    for client_info in clients.values():
        if client_info["address"] != addr:
            try:
                client_socket = client_info["socket"]
                client_socket.send(message)
            except Exception as e:
                print(f"Error enviando mensaje a {client_info['address']}: {e}")                                                                                                                                                                                                                                                   

def remove_client(addr):
    for username, client_info in list(clients.items()):
        if client_info["address"] == addr:
            del clients[username]
            print(f"Cliente {username} desconectado")

if __name__ == "__main__":
    while True:
        try:
            client, addr = server.accept()
            threading.Thread(target=handle_client, args=(client, addr)).start()
        except Exception as e:
            print(f"Error aceptando conexion: {e}")