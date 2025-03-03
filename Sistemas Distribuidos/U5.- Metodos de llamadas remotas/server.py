import threading
import socket
import json

class Server:
    def __init__(self, host='127.0.0.1'):
        self.host = host
        self.port = 0
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.lock = threading.Lock()
        self.players = {}
        self.connections = []

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.port = self.server_socket.getsockname()[1]
        print(f"Servidor escuchando en {self.host}:{self.port}")

        while True:
            conn, addr = self.server_socket.accept()
            print(f"Conexión aceptada de {addr}")
            self.connections.append(conn)  # Almacenar la conexión del cliente
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, conn, addr):
        with conn:
            try:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    message = json.loads(data.decode('utf-8'))
                    response = self.process_request(message, addr)
                    if response and message.get('method') == 'set_username':
                        data = json.dumps(response).encode('utf-8')
                        conn.sendall(data)
                    if response and message.get('method') == 'make_move':
                        data = json.dumps(response).encode('utf-8')
                        for connection in self.connections:
                            connection.sendall(data) 
            except Exception as e:
                print(f"Error manejando cliente: {e}")
            finally:
                if conn in self.connections:
                    self.connections.remove(conn)  # Remover la conexión al cerrar

    def process_request(self, request, addr):
        method = request.get('method')
        params = request.get('params', {})

        if method == 'set_username':
            return self.set_username(params, addr)
        elif method == 'make_move':
            return self.make_move(params)
        elif method == 'check_winner':
            return self.check_winner()
        elif method == 'check_draw':
            return self.check_draw()
        elif method == 'reset_board':
            return self.reset_board()
        elif method == 'get_board':
            return {'board': self.board}
        else:
            return {'error': 'Método desconocido'}

    def set_username(self, params, addr):
        username = params.get('username')
        if username in self.players:
            return {'status': 'Error', 'message': 'Nombre de usuario ya en uso'}
        with self.lock:
            if len(self.players) < 2:
                self.players[username] = addr
                player_symbol = 'X' if len(self.players) == 1 else 'O'
                return {'status': 'OK', 'player': player_symbol, 'current_player': self.current_player}
            else:
                return {'status': 'Error', 'message': 'El juego ya está lleno'}

    def make_move(self, params):
        row = params.get('row')
        col = params.get('col')
        player = params.get('player')
        with self.lock:
            if self.board[row][col] == '' and self.current_player == player:
                self.board[row][col] = player
                if self._check_winner(player):
                    return {'status': 'OK', 'winner': player, 'board': self.board}
                elif all(self.board[i][j] != '' for i in range(3) for j in range(3)):
                    return {'status': 'OK', 'draw': True, 'board': self.board}
                else:
                    self.current_player = 'O' if player == 'X' else 'X'
                    return {'status': 'OK', 'board': self.board, 'current_player': self.current_player}
            else:
                return {'status': 'Error', 'message': 'Movimiento inválido o no es tu turno'}

    def _check_winner(self, player):
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)) or \
               all(self.board[j][i] == player for j in range(3)):
                return True
        if all(self.board[i][i] == player for i in range(3)) or \
           all(self.board[i][2-i] == player for i in range(3)):
            return True
        return False

    def send_response_to_clients(self, message):
        for conn in self.connections:
            try:
                conn.sendall(json.dumps(message).encode('utf-8'))
            except Exception as e:
                print(f"Error enviando mensaje a un cliente: {e}")

    def run(self):
        pass

if __name__ == '__main__':
    server = Server()
    threading.Thread(target=server.start_server).start()
