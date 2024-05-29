import socket
import threading

HOST = '127.0.0.1'  # Localhost
PORT = 6789        # Port to listen on

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

# Handle individual client connection
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if message:
                broadcast(message)
            else:
                index = clients.index(client)
                nickname = nicknames[index]
                broadcast(f'{nickname} has left the chat!\n'.encode('ascii'))
                remove_client(client, nickname)
                break
        except:
            break


# Accepting new connections
def receive():
    while True:

        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # client.send('NICK'.encode('ascii'))
        # nickname = client.recv(1024).decode('ascii')
        # nicknames.append(nickname)

        clients.append(client)

        # print(f"Nickname of the client is {nickname}")
        # broadcast(f"{nickname} joined the chat!\n".encode('ascii'))
        # client.send('Connected to the server!\n'.encode('ascii'))

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print("Server is listening...")
receive()