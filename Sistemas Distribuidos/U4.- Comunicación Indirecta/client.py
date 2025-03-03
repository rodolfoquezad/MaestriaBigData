import threading
import socket
import argparse
import os
import sys
import tkinter as tk

class Send(threading.Thread):

    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):

        while True:
            print('{}: '.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            if message == "QUIT":
                self.sock.sendall('Server: {} ha salido del chat'.format(self.name).encode('ascii'))
                break

            else:
                self.sock.sendall('Server: {}: {} '.format(self.name, message).encode('ascii'))

        print('\nSaliendo del chat...')
        self.sock.close()
        os.exit(0)

class Recieve(threading.Thread):

    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None

    def run(self):

        while True:
            message = self.sock.recv(1024).decode('ascii')

            if message: 
                if self.messages:
                    self.messages.insert(tk.END, message)
                    print('\r{}\n{}: '.format(message, self.name), end='')

                else:
                    print('\r{}\n{}: '.format(message, self.name), end='')
            
            else:
                print('\n No. Perdimos conexión al servidor!')
                print('\nSaliendo del chat...')


class Client:

    def __init__(self, host, port):
        
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None

    def start(self):

        print('Intentando conectarse a {}:{}...'.format(self.host, self.port))

        self.sock.connect((self.host, self.port))

        print('Conectado exitosamente a {}:{}'.format(self.host,self.port))
        print()

        self.name = input('Ingrese su nombre: ')
        print()

        print('Bienvenido!, {} casi listo para enviar y recibir mensajes'. format(self.name))

        send = Send(self.sock, self.name)
        recieve = Recieve(self.sock, self.name)

        send.start()
        recieve.start()

        self.sock.sendall('{} Se ha unido al chat'.format(self.name).encode('ascii'))
        print("\n Listo para chatear!, puedes salir cuando quieras ingresando la palabra QUIT")
        print('{}:'.format(self.name),end='')

        return recieve

    def send(self, textInput):

        message = textInput.get()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, '{}: {}'.format(self.name, message))

        if message == "QUIT":
            self.sock.sendall('Servidor: {} a salido del chat'.format(self.name).encode('ascii'))
            print('\nSaliendo del chat...')
            self.sock.close()
            os.exit(0)

        else:
            self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))

def main(host, port):
    
    client = Client(host, port)
    recieve = client.start()

    window = tk.Tk()
    window.title("What's app killer")

    fromMessage = tk.Frame(master=window)
    scrollBar = tk.Scrollbar(master=fromMessage)
    messages = tk.Listbox(master=fromMessage, yscrollcommand= scrollBar.set)
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    client.messages = messages
    recieve.messages = messages

    fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)
    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind("<Return>", lambda x: client.send(textInput))
    textInput.insert(0, "Ingresa aquí tu mensaje")

    btnSend = tk.Button(master=window, text='Enviar', command= lambda: client.send(textInput))

    fromEntry.grid(row=1, column=0, padx=10, sticky="ew")
    btnSend.grid(row=1, column=1, pady=10, sticky="ew")

    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    window.mainloop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Servidor Chatroom")
    parser.add_argument('host', help='Interfaz donde el servidor escucha')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port(default 1060)')

    args = parser.parse_args()

    main(args.host, args.p)
