import socket
import threading
import tkinter as tk
import os
from tkinter import filedialog
from tkinter import messagebox, simpledialog
from cryptography.fernet import Fernet

# Cargar la clave desde el archivo
with open("fernet_key.key", "rb") as key_file:
    KEY = key_file.read()

cipher_suite = Fernet(KEY)

class Server:
    def __init__(self, host='127.0.0.1', port=0):
        self.host = host
        self.server_port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peers = []
        self.lock = threading.Lock()

    def start_server(self):
        self.server.bind((self.host, self.server_port))
        self.server_port = self.server.getsockname()[1]
        print(f"Servidor a la espera de conexiones en {self.host}:{self.server_port}\n")
        self.server.listen()
        while True:
            conn, addr = self.server.accept()
            with self.lock:
                self.peers.append(conn)
            print(f"Usuario conectado desde {addr}")
            threading.Thread(target=self.handle_client, args=(conn,)).start()

    def handle_client(self, conn):
        while True:
            try:
                file_name = conn.recv(1024).decode('utf-8')
                if file_name:
                    file_size = int(conn.recv(1024).decode('utf-8'))
                    print(f"Recibiendo archivo: {file_name} de tamaño {file_size} bytes")

                    save_path = os.path.join("C:\\Tareas\\Archivos_Recibidos\\", file_name)

                    with open(save_path, 'wb') as file:
                        received_size = 0
                        while received_size < file_size:
                            encrypted_data = conn.recv(1024)
                            if not encrypted_data:
                                break
                            received_size += len(encrypted_data)
                            print(f"Received encrypted data: {encrypted_data}")
                            decrypted_data = cipher_suite.decrypt(encrypted_data)
                            file.write(decrypted_data)
                    print(f"Archivo {file_name} recibido y guardado en {save_path}")
            except ConnectionResetError:
                with self.lock:
                    self.peers.remove(conn)
                break
            except Exception as e:
                print(f"Error durante la recepción o desencriptación: {e}")
                break

class Client:
    def __init__(self):
        self.connection = False
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        try:
            self.client.connect((host, port))
            print(f"Conectado al servidor {host}:{port}")
            self.connection = True
            return True
        except Exception as e:
            print(f"Error al conectar al servidor: {e}")
            self.connection = False
            return False

    def send_file(self, file_path):
        try:
            file_name = file_path.split("/")[-1]
            file_size = os.path.getsize(file_path)
            self.client.send(file_name.encode('utf-8'))
            self.client.send(str(file_size).encode('utf-8'))

            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    encrypted_data = cipher_suite.encrypt(data)
                    print(f"Sending encrypted data: {encrypted_data}")
                    self.client.send(encrypted_data)

            print(f"Archivo {file_name} enviado correctamente.")
        except Exception as e:
            print(f"Error al enviar el archivo: {e}")

def main():
    server = Server()
    server_thread = threading.Thread(target=server.start_server, daemon=True)
    server_thread.start()

    root = tk.Tk()
    app = FileSenderApp(root)
    root.mainloop()

    while True:
        pass

class FileSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enviar Archivo")
        self.root.geometry("400x150")

        self.client = Client()

        self.connect_button = tk.Button(root, text="Conectar a Servidor", command=self.connect_to_server)
        self.connect_button.pack(pady=10)

        self.send_button = tk.Button(root, text="Seleccionar y Enviar Archivo", command=self.select_and_send_file)
        self.send_button.pack(pady=10)

    def connect_to_server(self):
        host = simpledialog.askstring("Conectar a Servidor", "Ingresa la dirección IP del servidor:", initialvalue="127.0.0.1")
        port = simpledialog.askinteger("Conectar a Servidor", "Ingresa el puerto del servidor:", initialvalue=5000)

        if host and port:
            if self.client.connect(host, port):
                messagebox.showinfo("Conexión Exitosa", f"Conectado al servidor {host}:{port}")
            else:
                messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor {host}:{port}")

    def select_and_send_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if not self.client.connection:
                messagebox.showerror("Error", "No estás conectado a un servidor.")
                return

            self.client.send_file(file_path)
            messagebox.showinfo("Éxito", "Archivo enviado correctamente.")

if __name__ == "__main__":
    main()