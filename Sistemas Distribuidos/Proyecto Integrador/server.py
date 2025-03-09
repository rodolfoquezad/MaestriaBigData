import socket
import threading

class Server:

    def __init__(self):
        self.clients = {} 
        self.usernames = [] 
        self.groups = {}

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 1001))
        server.listen()
        print("Servidor en espera de conexiones...")

        while True:
            client_socket, addr = server.accept()
            username = client_socket.recv(1024).decode('utf-8')
            self.clients[username] = client_socket
            self.usernames.append(username)
            print(f"{username} se ha conectado desde {addr}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, username))
            client_thread.start()

    def handle_client(self, client_socket, username):
        self.broadcast_users_list()
        self.send_user_groups(username)
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message.startswith("/private"):
                    _, recipient, private_message = message.split(' ', 2)
                    self.send_private_message(username, recipient, private_message)
                elif message.startswith("/creategroup"):
                    _, group_name = message.split(' ', 1)
                    self.create_group(group_name, username)
                elif message.startswith("/addtogroup"):
                    _, group_name, member = message.split(' ', 2)
                    self.add_to_group(group_name, member, username)
                elif message.startswith("/groupmsg"):
                    _, group_name, group_message = message.split(' ', 2)
                    self.send_group_message(username, group_name, group_message)
            except:
                break

        client_socket.close()
        del self.clients[username]
        self.usernames.remove(username)
        self.broadcast_users_list()

    def send_private_message(self, sender, recipient, message):
        if recipient in self.clients:
            try:
                self.clients[recipient].send(f"{message}".encode('utf-8'))
            except:
                self.clients[recipient].close()

    def create_group(self, group_name, creator):
        if group_name not in self.groups:
            self.groups[group_name] = [creator]
            self.clients[creator].send(f"Grupo '{group_name}' creado con éxito.".encode('utf-8'))
            self.send_user_groups(creator) 
        else:
            self.clients[creator].send(f"El grupo '{group_name}' ya existe.".encode('utf-8'))

    def add_to_group(self, group_name, member, requester):
        if group_name in self.groups:
            if requester in self.groups[group_name]:
                if member in self.usernames:
                    if member not in self.groups[group_name]:
                        self.groups[group_name].append(member)
                        self.clients[member].send(f"Has sido añadido al grupo '{group_name}'.".encode('utf-8'))
                        self.send_user_groups(member)
                    else:
                        self.clients[requester].send(f"El usuario '{member}' ya está en el grupo.".encode('utf-8'))
                else:
                    self.clients[requester].send(f"El usuario '{member}' no existe.".encode('utf-8'))
            else:
                self.clients[requester].send(f"No tienes permiso para añadir miembros al grupo '{group_name}'.".encode('utf-8'))
        else:
            self.clients[requester].send(f"El grupo '{group_name}' no existe.".encode('utf-8'))

    def send_group_message(self, sender, group_name, message):
        if group_name in self.groups:
            if sender in self.groups[group_name]:
                for member in self.groups[group_name]:
                    try:
                        self.clients[member].send(f"{sender}: {message}".encode('utf-8'))
                    except:
                        self.clients[member].close()
            else:
                self.clients[sender].send(f"No eres miembro del grupo '{group_name}'.".encode('utf-8'))
        else:
            self.clients[sender].send(f"El grupo '{group_name}' no existe.".encode('utf-8'))

    def broadcast_users_list(self):
        users_list_message = "USERS_LIST " + " ".join(self.usernames)
        for client in self.clients.values():
            try:
                client.send(users_list_message.encode('utf-8'))
            except:
                client.close()

    def send_user_groups(self, username):
        user_groups = [group for group, members in self.groups.items() if username in members]
        groups_list_message = "GROUPS_LIST " + " ".join(user_groups)
        if username in self.clients:
            try:
                self.clients[username].send(groups_list_message.encode('utf-8'))
            except:
                self.clients[username].close()

def main():
    server = Server()
    server.start_server()

if __name__ == '__main__':
    main()