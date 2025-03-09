import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

class Client:
    def __init__(self, root):
        self.root = root
        
        self.users_frame = tk.Frame(root)
        self.users_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.users_listbox = tk.Listbox(self.users_frame)
        self.users_listbox.pack(fill=tk.BOTH, expand=True)
        self.users_listbox.bind("<<ListboxSelect>>", self.on_user_or_group_select)
        
        self.chat_frame = tk.Frame(root)
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD)
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)
        
        self.msg_entry = tk.Entry(self.chat_frame)
        self.msg_entry.pack(fill=tk.X, pady=(0, 10))
        self.msg_entry.bind("<Return>", self.send_message)
        
        self.create_group_button = tk.Button(self.users_frame, text="Crear Grupo", command=self.create_group)
        self.create_group_button.pack(fill=tk.X, pady=(0, 10))
        
        self.add_user_button = tk.Button(self.users_frame, text="Agregar Usuario al Grupo", command=self.add_user_to_group)
        self.add_user_button.pack(fill=tk.X, pady=(0, 10))
        self.add_user_button.config(state=tk.DISABLED)  # Inicialmente deshabilitado
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 1001))
        
        self.username = simpledialog.askstring("Nombre de usuario", "Por favor, introduce tu nombre de usuario:")
        self.root.title(f"Proyecto Integrador: {self.username}")
        self.client_socket.send(self.username.encode('utf-8'))
        
        self.selected_user = None
        self.selected_group = None
        self.chat_history = {}
        self.group_chat_history = {}
        self.all_users = [] 
        self.user_groups = [] 
        
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()
    
    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("USERS_LIST"):
                    users = message.split()[1:]
                    self.all_users = users
                    self.update_users_and_groups_list()
                elif message.startswith("GROUPS_LIST"):
                    groups = message.split()[1:]
                    self.user_groups = groups 
                    self.update_users_and_groups_list()
                elif message.startswith("(Privado)"):
                    sender = message.split(":")[0].split()[1]
                    if sender not in self.chat_history:
                        self.chat_history[sender] = []
                    self.chat_history[sender].append(message)
                    
                    if self.selected_user == sender:
                        self.display_message(message)
                elif message.startswith("(Grupo"):
                    group_name = message.split("'")[1]
                    if group_name not in self.group_chat_history:
                        self.group_chat_history[group_name] = []
                    self.group_chat_history[group_name].append(message)
                    
                    if self.selected_group == group_name:
                        self.display_message(message)
            except:
                break

    def send_message(self, event=None):
        if not self.selected_user and not self.selected_group:
            messagebox.showwarning("Selección", "Debes seleccionar un usuario o grupo para enviar un mensaje.")
            return
        
        message = self.msg_entry.get()
        if message:
            if self.selected_user:
                self.client_socket.send(f"/private {self.selected_user} {message}".encode('utf-8'))
                
                if self.selected_user not in self.chat_history:
                    self.chat_history[self.selected_user] = []
                self.chat_history[self.selected_user].append(f"{message}")
                
                self.display_message(f"{message}")
            elif self.selected_group:
                self.client_socket.send(f"/groupmsg {self.selected_group} {message}".encode('utf-8'))
                
                if self.selected_group not in self.group_chat_history:
                    self.group_chat_history[self.selected_group] = []
                self.group_chat_history[self.selected_group].append(f"{message}")
                
                self.display_message(f"{message}")
            self.msg_entry.delete(0, tk.END)
    
    def display_message(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)

    def update_users_and_groups_list(self):
        self.users_listbox.delete(0, tk.END)
        for user in self.all_users:
            if user != self.username:
                self.users_listbox.insert(tk.END, user)
        for group in self.user_groups:
            self.users_listbox.insert(tk.END, group)

    def on_user_or_group_select(self, event):
        selection = event.widget.curselection()
        if selection:
            selected_item = event.widget.get(selection[0])
            if selected_item in self.all_users:
                self.selected_user = selected_item
                self.selected_group = None
                self.add_user_button.config(state=tk.DISABLED)
            else:
                self.selected_group = selected_item
                self.selected_user = None
                self.add_user_button.config(state=tk.NORMAL)
            
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.delete(1.0, tk.END)
            self.chat_area.config(state=tk.DISABLED)
            
            if self.selected_user:
                if self.selected_user in self.chat_history:
                    for message in self.chat_history[self.selected_user]:
                        self.display_message(message)
            elif self.selected_group:
                if self.selected_group in self.group_chat_history:
                    for message in self.group_chat_history[self.selected_group]:
                        self.display_message(message)

    def create_group(self):
        group_name = simpledialog.askstring("Crear Grupo", "Introduce el nombre del grupo:")
        if group_name:
            self.client_socket.send(f"/creategroup {group_name}".encode('utf-8'))

    def add_user_to_group(self):
        if not self.selected_group:
            messagebox.showwarning("Selección", "Debes seleccionar un grupo para agregar usuarios.")
            return
        user_to_add = simpledialog.askstring("Agregar Usuario", "Introduce el nombre del usuario a agregar:")
        if user_to_add:
            if user_to_add in self.all_users:
                self.client_socket.send(f"/addtogroup {self.selected_group} {user_to_add}".encode('utf-8'))
            else:
                messagebox.showwarning("Error", f"El usuario '{user_to_add}' no está conectado.")

def main():
    root = tk.Tk()
    client = Client(root)
    root.mainloop()

if __name__ == '__main__':
    main()