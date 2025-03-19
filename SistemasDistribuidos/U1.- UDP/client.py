import socket

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 10001
    addr = (host,port)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        data = "¡¡¡HOLA MUNDO!!!"
        data = data.encode("utf-8")
        client.sendto(data, addr)

        # Recibir respuesta del servidor (buffer de 1024 bytes)
        data, server = client.recvfrom(1024)
        print(f"Respuesta del servidor: {data.decode('utf-8')}")
        break
    client.close()
    