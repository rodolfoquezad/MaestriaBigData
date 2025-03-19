import socket

host = "127.0.0.1"
port = 10001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
    socket.connect((host,port))
    data = "¡¡¡HOLA MUNDO!!!"
    data = data.encode("utf-8")
    socket.sendall(data)
    data = socket.recv(1024)


print(f"Respuesta del servidor: {data.decode("utf-8")}")
