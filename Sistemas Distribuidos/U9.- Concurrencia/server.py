import socket
import threading

HOST = 'localhost'
PORT = 1001

def handle_client(client_socket, client_address):
    print(f"Conexión establecida con {client_address}")
    
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            for client in clients:
                if client != client_socket:
                    client.send(data)
        
        except ConnectionResetError:
            break
    
    print(f"Conexión cerrada con {client_address}")
    clients.remove(client_socket)
    client_socket.close()

clients = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Servidor escuchando en {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()