import socket
import threading
import os
from cryptography.fernet import Fernet


KEY = b'T6-LALEyMf1tKdF40Iu48acmO23l4nR5toitrue6TUs='
cipher_suite = Fernet(KEY)

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
                message_type = client_socket.recv(1024).decode('utf-8')
                if not message_type:
                    break
                if message_type.startswith("/privatefile"):
                    _, recipient = message_type.split(' ', 1)
                    file_name = b""
                    while True:
                        chunk = client_socket.recv(1)
                        if chunk == b'\n':
                            break
                        file_name += chunk
                    try:
                        file_name = file_name.decode('utf-8')
                        self.receive_file(client_socket, username, recipient, file_name)
                    except UnicodeDecodeError as e:
                        print(f"[ERROR] No se pudo decodificar el nombre del archivo: {e}")
                elif message_type.startswith("/groupfile"):
                    _, group_name = message_type.split(' ', 1)
                    file_name = b""
                    while True:
                        chunk = client_socket.recv(1)
                        if chunk == b'\n':
                            break
                        file_name += chunk
                    try:
                        file_name = file_name.decode('utf-8')
                        self.receive_group_file(client_socket, username, group_name, file_name)
                    except UnicodeDecodeError as e:
                        print(f"[ERROR] No se pudo decodificar el nombre del archivo: {e}")
                elif message_type.startswith("/private"):
                    parts = message_type.split(' ', 2)
                    if len(parts) == 3:
                        _, recipient, private_message = parts
                        self.send_private_message(username, recipient, private_message)
                    else:
                        print(f"[ERROR] Invalid private message format: {message_type}")
                elif message_type.startswith("/creategroup"):
                    _, group_name = message_type.split(' ', 1)
                    self.create_group(group_name, username)
                elif message_type.startswith("/addtogroup"):
                    _, group_name, member = message_type.split(' ', 2)
                    self.add_to_group(group_name, member, username)
                elif message_type.startswith("/groupmsg"):
                    _, group_name, group_message = message_type.split(' ', 2)
                    self.send_group_message(username, group_name, group_message)

            except Exception as e:
                print(f"Error: {e}")
                break

        client_socket.close()
        del self.clients[username]
        self.usernames.remove(username)
        self.broadcast_users_list()

    def send_private_message(self, sender, recipient, encrypted_message):
        if recipient in self.clients:
            try:
                self.clients[recipient].send(f"(Privado) {sender}: {encrypted_message}".encode('utf-8'))
            except:
                self.clients[recipient].close()

    def send_group_message(self, sender, group_name, encrypted_message):
        if group_name in self.groups:
            if sender in self.groups[group_name]:
                for member in self.groups[group_name] and member != sender:
                    try:
                        self.clients[member].send(f"(Grupo '{group_name}') {sender}: {encrypted_message}".encode('utf-8'))
                    except:
                        self.clients[member].close()
            else:
                self.clients[sender].send(f"No eres miembro del grupo '{group_name}'.".encode('utf-8'))
        else:
            self.clients[sender].send(f"El grupo '{group_name}' no existe.".encode('utf-8'))

    def send_group_message(self, sender, group_name, encrypted_message):
        if group_name in self.groups:
            if sender in self.groups[group_name]:
                for member in self.groups[group_name]:
                    try:
                        self.clients[member].send(f"(Grupo '{group_name}') {sender}: {encrypted_message}".encode('utf-8'))
                    except:
                        self.clients[member].close()
            else:
                self.clients[sender].send(f"No eres miembro del grupo '{group_name}'.".encode('utf-8'))
        else:
            self.clients[sender].send(f"El grupo '{group_name}' no existe.".encode('utf-8'))

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

    def receive_file(self, client_socket, sender, recipient, file_name):
        if recipient in self.clients:
            try:
                save_path = f"C:\\Archivos_Recibidos\\{recipient}"
                os.makedirs(save_path, exist_ok=True)
                
                file_path = os.path.join(save_path, file_name)
                with open(file_path, "wb") as file:
                    while True:
                        file_data = client_socket.recv(4096)
                        if not file_data:
                            break
                        if file_data.endswith(b"<END_OF_FILE>"):
                            file.write(file_data[:-len(b"<END_OF_FILE>")])
                            break
                        else:
                            file.write(file_data)
                self.clients[recipient].send(f"FILE_RECEIVED:{file_name}".encode('utf-8'))
            except Exception as e:
                print(f"[ERROR] Error al recibir archivo: {e}")
        else:
            self.clients[sender].send(f"El usuario '{recipient}' no está conectado.".encode('utf-8'))

    def receive_group_file(self, client_socket, sender, group_name, file_name):
        if group_name in self.groups:
            if sender in self.groups[group_name]:
                temp_file_path = f"C:\\Archivos_Recibidos\\{group_name}_{file_name}"
                with open(temp_file_path, "wb") as temp_file:
                    while True:
                        file_data = client_socket.recv(4096)
                        if not file_data:
                            break
                        
                        if file_data.endswith(b"<END_OF_FILE>"):
                            temp_file.write(file_data[:-len(b"<END_OF_FILE>")])
                            break
                        else:
                            temp_file.write(file_data)
                
                for member in self.groups[group_name]:
                    if member != sender:
                        try:
                            save_path = f"C:\\Archivos_Recibidos\\{member}"
                            os.makedirs(save_path, exist_ok=True)
                            
                            file_path = os.path.join(save_path, file_name)
                            with open(temp_file_path, "rb") as temp_file, open(file_path, "wb") as file:
                                while True:
                                    file_data = temp_file.read(4096)
                                    if not file_data:
                                        break
                                    file.write(file_data)
                            
                            self.clients[member].send(f"FILE_RECEIVED:{file_name}".encode('utf-8'))
                        except Exception as e:
                            print(f"[ERROR] Error al recibir archivo para {member}: {e}")
                
                os.remove(temp_file_path)
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