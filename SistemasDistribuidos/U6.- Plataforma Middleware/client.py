import tkinter as tk
from tkinter import messagebox
import socket
import json
import threading

host = "127.0.0.1"
port = 1001

class Player:
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.position = (0, 0)
        self.root = None
        self.canvas = None
        self.photo_image = None
        self.game_started = False
        self.overlay_label = None

    def connect(self):
        print(f"Intentando conectarse a {self.host}:{self.port}")
        try:
            self.client.connect((self.host, self.port))
            print(f"Conectado exitosamente a {self.host}:{self.port}")
            self.client.send(self.username.encode())
            self.position = tuple(map(int, self.client.recv(1024).decode().split(',')))
            self.receive_updates()
            return True
        except Exception as e:
            print(f"Error al conectarse: {e}")
            return False

    def send_move(self, direction):
        if self.game_started:
            self.client.send(direction.encode())

    def receive_updates(self):
        def update():
            buffer = ""
            while True:
                try:
                    data = self.client.recv(1024).decode()
                    if data:
                        buffer += data
                        while "\n" in buffer:
                            message, buffer = buffer.split("\n", 1)
                            if message == "WAITING_FOR_PLAYERS":
                                print(f"Esperando jugadores...")
                            elif message == "GAME_STARTED":
                                print("¡El juego ha comenzado!")
                                if self.overlay_label and self.overlay_label.winfo_ismapped():
                                    self.overlay_label.place_forget()
                                self.game_started = True
                            elif message.startswith("GAME_OVER"):
                                print(f"El juego ha terminado. Ganador: {message.split(':')[1]}")
                                self.root.quit()
                                break
                            elif message == "YOU_ARE_ELIMINATED":
                                messagebox.showinfo("Juego Terminado!", "Fuiste eliminado!")
                                self.root.quit()
                                break
                            else:
                                try:
                                    game_state = json.loads(message)
                                    self.update_ui(game_state)
                                except json.JSONDecodeError as e:
                                    print(f"Error decoding JSON: {e}")
                    else:
                        break
                except Exception as e:
                    print(f"Error: {e}")
                    break

        threading.Thread(target=update).start()

    def create_ui(self):
        GRID_SIZE = 20
        CELL_SIZE = 50

        self.root = tk.Tk()
        self.root.title(f"Pacman, jugador {self.username}")

        self.canvas = tk.Canvas(self.root, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE)
        self.canvas.pack()

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x0, y0 = j * CELL_SIZE, i * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black")

        self.root.bind("<Up>", lambda event: self.send_move("up"))
        self.root.bind("<Down>", lambda event: self.send_move("down"))
        self.root.bind("<Left>", lambda event: self.send_move("left"))
        self.root.bind("<Right>", lambda event: self.send_move("right"))

        self.overlay_label = tk.Label(
            self.root,
            text="Esperando más jugadores...",
            font=("Arial", 24),
            bg="yellow",
            fg="black"
        )

        self.overlay_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.root.mainloop()

    def update_ui(self, game_state):
        if self.overlay_label and self.overlay_label.winfo_ismapped():
            self.overlay_label.place_forget()

        self.canvas.delete("all")

        GRID_SIZE = 20
        CELL_SIZE = 50

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x0, y0 = j * CELL_SIZE, i * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black")

        for username, ((x, y), is_hunter) in game_state["players"].items():
            color = "red" if is_hunter else "yellow"
            self.canvas.create_oval(x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE, fill=color, tags="player")

        if game_state["coin"]:
            x, y = game_state["coin"]
            self.canvas.create_oval(x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE, fill="green", tags="coin")

def main(host, port):
    username = input('Ingresa tu nombre de jugador: ')
    player = Player(host, port, username)
    if player.connect():
        player.create_ui()
        return True

if __name__ == "__main__":
    main(host, port)
