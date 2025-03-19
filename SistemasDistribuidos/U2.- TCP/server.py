import socket

host = "127.0.0.1"
port = 10001
clients = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
    socket.bind((host,port))
    socket.listen()
    print(f"Servidor esperando conexion en {host}, {port}")
    conn, addr = socket.accept()
    with conn:
        clients=+1
        print(f"Conectado por {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
            