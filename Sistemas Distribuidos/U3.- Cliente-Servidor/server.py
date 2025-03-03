import socket
import threading

clients = {}
usernames = []

def handle_client(client_socket, username):
    broadcast_users_list()
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message.startswith("/private"):
                _, recipient, private_message = message.split(' ', 2)
                send_private_message(username, recipient, private_message)
        except:
            break

    client_socket.close()
    del clients[username]
    usernames.remove(username)
    broadcast_users_list()


def send_private_message(sender, recipient, message):
    if recipient in clients:
        try:
            clients[recipient].send(f"(Privado) {sender}: {message}".encode('utf-8'))
        except:
            clients[recipient].close()

def broadcast_users_list():
    users_list_message = "USERS_LIST " + " ".join(usernames)
    for client in clients.values():
        try:
            client.send(users_list_message.encode('utf-8'))
        except:
            client.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))
server.listen(5)
print("Servidor en espera de conexiones...")

while True:
    client_socket, addr = server.accept()
    username = client_socket.recv(1024).decode('utf-8')
    clients[username] = client_socket
    usernames.append(username)
    print(f"{username} se ha conectado desde {addr}")
    client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
    client_thread.start()
