import socket

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 10001

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server.bind((host, port))
    print("Servidor UDP en espera......")

    while True:
        data, addr = server.recvfrom(1024)
        print(f"Recibido de cliente: {data.decode("utf-8")}")
        server.sendto(data,addr)
        