import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat TCP")
        
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)
        
        self.users_listbox = tk.Listbox(root)
        self.users_listbox.pack(padx=10, pady=10, fill=tk.Y, side=tk.RIGHT)
        self.users_listbox.bind("<<ListboxSelect>>", self.on_user_select)
        
        self.msg_entry = tk.Entry(root)
        self.msg_entry.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.msg_entry.bind("<Return>", self.send_message)
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))
        
        self.username = simpledialog.askstring("Nombre de usuario", "Por favor, introduce tu nombre de usuario:")
        self.client_socket.send(self.username.encode('utf-8'))
        
        self.selected_user = None
        
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()


        self.port_entry = tk.Entry(self.root)
        self.port_entry.grid(row=0, column=3, padx=10)
        connect_button = tk.Button(self.root, text="Conectar", command=self.connect_to_server)
        connect_button.grid(row=1, column=3, padx=10)

        self.users_listbox = tk.Listbox(root)
        self.users_listbox.grid(row=2, column=3, rowspan=3, padx=10)
        self.users_listbox.insert(tk.END, f"{self.username}")
    
    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("USERS_LIST"):
                    users = message.split()[1:]
                    self.update_users_list(users)
                else:
                    self.display_message(message)
            except:
                break

    def send_message(self, event=None):
        if not self.selected_user:
            messagebox.showwarning("Selección de usuario", "Debes seleccionar un usuario de la lista para enviar un mensaje.")
            return
        
        message = self.msg_entry.get()
        if message:
            self.client_socket.send(f"/private {self.selected_user} {message}".encode('utf-8'))
            self.display_message(f"(Privado a {self.selected_user}): {message}")
        self.msg_entry.delete(0, tk.END)
    
    def display_message(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)

    def update_users_list(self, users):
        self.users_listbox.delete(0, tk.END)
        for user in users:
            if user != self.username:
                self.users_listbox.insert(tk.END, user)

    def on_user_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.selected_user = event.widget.get(selection[0])
            messagebox.showinfo("Usuario seleccionado", f"Has seleccionado a {self.selected_user} para chat privado.")

root = tk.Tk()
client = ChatClient(root)
root.mainloop()
