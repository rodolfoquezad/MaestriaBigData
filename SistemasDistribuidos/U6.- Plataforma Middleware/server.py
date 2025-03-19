import socket
import threading
import random
import json
import time

host = "127.0.0.1"
port = 1001

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players = {}
        self.coin_position = None
        self.game_over = False 
        self.min_players = 4
        self.game_started = False 
        self.lock = threading.Lock()
        self.coin_respawn_time = time.time()

    def handle_client(self, conn, addr):
        username = conn.recv(1024).decode()
        print(f"Jugador {username} se ha conectado")

        x, y = random.randint(0, 19), random.randint(0, 19)
        with self.lock:
            self.players[addr] = (conn, username, (x, y), False)
        conn.send(f"{x},{y}\n".encode())  

        if len(self.players) < self.min_players:
            conn.send("WAITING_FOR_PLAYERS\n".encode())  
        else:
            if not self.game_started:
                self.game_started = True
                self.coin_position = (random.randint(0, 19), random.randint(0, 19))
                self.notify_game_started()
                threading.Thread(target=self.game_loop).start()
            else:
                self.notify_game_started()
                threading.Thread(target=self.game_loop).start()

        while not self.game_over:
            try:
                data = conn.recv(1024).decode()
                if data:
                    direction = data.strip()
                    self.move_player(addr, direction)
            except Exception as e:
                print(f"Error: {e}")
                break
            if addr not in self.players:
                break
        conn.close()

    def move_player(self, addr, direction):
        with self.lock:
            conn, username, (x, y), is_hunter = self.players[addr]
            if direction == "up" and y > 0:
                y -= 1
            elif direction == "down" and y < 19:
                y += 1
            elif direction == "left" and x > 0:
                x -= 1
            elif direction == "right" and x < 19:
                x += 1
            self.players[addr] = (conn, username, (x, y), is_hunter)
            
            if (x, y) == self.coin_position:
                self.coin_position = None
                self.coin_respawn_time = time.time() + 10
                is_hunter = True
                self.players[addr] = (conn, username, (x, y), is_hunter)

    def check_collisions(self):
        with self.lock:
            positions = {addr: pos for addr, (conn, username, pos, is_hunter) in self.players.items()}
            to_remove = []
            for addr, pos in positions.items():
                for other_addr, other_pos in positions.items():
                    if addr != other_addr and pos == other_pos:
                        if self.players[addr][3]:
                            to_remove.append(other_addr)
                        elif self.players[other_addr][3]:
                            to_remove.append(addr)

            for addr in to_remove:
                if addr in self.players:
                    conn, username, pos, is_hunter = self.players[addr]
                    conn.send("YOU_ARE_ELIMINATED\n".encode())
                    del self.players[addr]

    def notify_game_started(self):
        with self.lock:
            message = "GAME_STARTED\n"
            for addr, (conn, username, pos, is_hunter) in self.players.items():
                try:
                    conn.send(message.encode())
                except Exception as e:
                    print(f"Error al iniciar juego: {e}")

    def broadcast_game_state(self):
        with self.lock:
            if len(self.players) == 1:
                self.game_over = True
                winner = list(self.players.values())[0][1]
                message = f"GAME_OVER:{winner}\n"
                self.update_clients(message)
            else:
                game_state = {
                    "players": {username: (pos, is_hunter) for addr, (conn, username, pos, is_hunter) in self.players.items()},
                    "coin": self.coin_position,
                    "game_started": self.game_started
                }
                message = json.dumps(game_state) + "\n"
                self.update_clients(message)

    def update_clients(self, message):
        time.sleep(0.2)  
        for addr, (conn, username, pos, is_hunter) in self.players.items():
            try:
                conn.send(message.encode())
            except Exception as e:
                print(f"Error al enviar datos al cliente: {e}")

    def game_loop(self):
        while not self.game_over:
            self.check_collisions()
            
            with self.lock:
                current_time = time.time()
                if not self.coin_position and current_time >= self.coin_respawn_time:
                    for addr, (conn, username, pos, is_hunter) in self.players.items():
                        if is_hunter:
                            self.players[addr] = (conn, username, pos, False)
                    self.coin_position = (random.randint(0, 19), random.randint(0, 19))

            self.broadcast_game_state()
            time.sleep(0.1)

    def start_server(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Servidor esperando conexión en {self.host}:{self.port}")

        while True:
            conn, addr = self.server.accept()
            print(f"Nueva conexión desde {addr}")
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

def main(host, port):
    server = Server(host, port)
    server.start_server()

if __name__ == "__main__":
    main(host, port)
