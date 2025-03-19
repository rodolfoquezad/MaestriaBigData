import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import vlc

HOST = 'localhost'
PORT = 1001

RECEIVED_VIDEOS_PATH = r"C:\Videos_Recibidos"

if not os.path.exists(RECEIVED_VIDEOS_PATH):
    os.makedirs(RECEIVED_VIDEOS_PATH)

vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()

def receive_data(client_socket):
    while True:
        try:
            file_name_data = client_socket.recv(1024)
            if not file_name_data:
                break
            
            file_name = file_name_data.decode().strip()
            file_path = os.path.join(RECEIVED_VIDEOS_PATH, file_name)

            with open(file_path, 'wb') as file:
                media = vlc_instance.media_new_path(file_path)
                player.set_media(media)
                player.play()

                while True:
                    bytes_read = client_socket.recv(1024)
                    if not bytes_read:
                        break
                    file.write(bytes_read)
                    file.flush()
            
            print(f"Video recibido y guardado en: {file_path}")
            messagebox.showinfo("Video Recibido", f"Video guardado en: {file_path}")
        
        except ConnectionResetError:
            break
        except Exception as e:
            print(f"Error al recibir el video: {e}")
            break
    
    client_socket.close()

def send_video(client_socket, file_path):
    try:
        file_name = os.path.basename(file_path)
        client_socket.sendall(file_name.encode())

        with open(file_path, 'rb') as file:
            while True:
                bytes_read = file.read(1024)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)
        
        messagebox.showinfo("Éxito", "Video enviado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al enviar el video: {e}")

def select_file(client_socket):
    file_path = filedialog.askopenfilename(
        title="Seleccionar video",
        filetypes=(("Archivos de video", "*.mp4 *.avi *.mkv"), ("Todos los archivos", "*.*"))
    )
    if file_path:
        send_video(client_socket, file_path)

def create_gui(client_socket):
    root = tk.Tk()
    root.title("Cliente de Video")

    select_button = tk.Button(root, text="Seleccionar y Enviar Video", command=lambda: select_file(client_socket))
    select_button.pack(pady=20)

    root.mainloop()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

receive_thread = threading.Thread(target=receive_data, args=(client_socket,))
receive_thread.start()

create_gui(client_socket)

client_socket.close()