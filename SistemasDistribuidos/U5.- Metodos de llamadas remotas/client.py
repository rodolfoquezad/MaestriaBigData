import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
import json

class Client:
    def __init__(self, root):
        self.root = root
        self.host = '127.0.0.1'
        self.port = simpledialog.askinteger("Puerto", "Ingresa el puerto del servidor:")
        self.username = simpledialog.askstring("Nombre de usuario", "Ingresa tu nombre de usuario:")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.player = ''
        self.current_player = ''
        self.connect_to_server()

        self.create_interface()
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def connect_to_server(self):
        self.client_socket.connect((self.host, self.port))
        print(f"Conectado al servidor en {self.host}:{self.port}")

        self.send_request({
            'method': 'set_username',
            'params': {
                'username': self.username
            }
        })

    def create_interface(self):
        self.root.title(f"Tic Tac Toe - {self.username}")
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(
                    self.root, text='', font=('Arial', 24), width=5, height=2,
                    command=lambda row=i, col=j: self.make_move(row, col)
                )
                self.buttons[i][j].grid(row=i, column=j)
        self.status_label = tk.Label(self.root, text="Esperando a otro jugador...", font=('Arial', 14))
        self.status_label.grid(row=3, column=0, columnspan=3)

    def make_move(self, row, col):
        move_request = {
            'method': 'make_move',
            'params': {
                'row': row,
                'col': col,
                'player': self.player
            }
        }
        self.send_request(move_request)

    def send_request(self, request):
        data = json.dumps(request).encode('utf-8')
        self.client_socket.sendall(data)

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                response = json.loads(data.decode('utf-8'))
                self.process_response(response)
            except Exception as e:
                print(f"Error recibiendo mensajes: {e}")
                break

    def process_response(self, response):
        if 'board' in response:
            self.board = response['board']
            self.update_board()
        if 'status' in response:
            if response['status'] == 'Error':
                messagebox.showerror("Error", response.get('message'))
            elif response['status'] == 'OK':
                pass 
        if 'winner' in response and response['winner']:
            winner = response['winner']
            messagebox.showinfo("Juego Terminado", f"¡{winner} ha ganado!")
            self.reset_game()
        if 'draw' in response and response['draw']:
            messagebox.showinfo("Juego Terminado", "¡Es un empate!")
            self.reset_game()
        if 'player' in response:
            self.player = response['player']
            self.status_label.config(text=f"Eres el jugador {self.player}")
        if 'current_player' in response:
            self.current_player = response['current_player']
            self.update_status()

    def update_board(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=self.board[i][j])

    def update_status(self):
        if self.player == self.current_player:
            self.status_label.config(text="Tu turno")
            self.enable_buttons()
        else:
            self.status_label.config(text=f"Turno del jugador {self.current_player}")
            self.disable_buttons()

    def reset_game(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.update_board()
        self.status_label.config(text="Esperando a otro jugador...")

    def disable_buttons(self):
        for row in self.buttons:
            for button in row:
                button.config(state=tk.DISABLED)

    def enable_buttons(self):
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == '':
                    self.buttons[i][j].config(state=tk.NORMAL)
                else:
                    self.buttons[i][j].config(state=tk.DISABLED)

    def run(self):
        pass

if __name__ == '__main__':
    root = tk.Tk()
    client = Client(root)
    root.mainloop()
