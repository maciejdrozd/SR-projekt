#Projekt zaliczeniowy - Systemy rozproszone
#Maciej Drozd, Matuesz Królak, Michał Raczkiewicz, Tomasz Kunicki
#Informatyka, semestr 5, st. niestacjonarne

import socket
import threading

HOST = '127.0.0.1'
PORT = 5050
FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []
messageStorage = {}

# transmitowanie wysyłanych wiadomości przez klientów
def broadcast(message, sendTo):
    print("Wysłano wiadomość do: " + sendTo)
    if sendTo == 'wszyscy':
        for client in clients:
            client.send(message)
    else:
        if sendTo.encode(FORMAT) in nicknames:
            for name in nicknames:
                decodedName = name.decode(FORMAT)
                if decodedName == sendTo:
                    clients[nicknames.index(name)].send(message)
                print(nicknames)
                print(messageStorage)
        else:
            messageStorage[sendTo] = message

# obsługa połączeń od klientów
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            # czy wiadomość jest wysłana do wszystkich czy do konkretnego klienta
            # żeby wysłać prywatną wiadomość należy najpierw podać nickname klienta a następnie 2x dwukropek
            # np. XYZ::
            decodedMessage = message.decode(FORMAT)
            if "::" in decodedMessage:
                sendToName = decodedMessage.partition(":")[0]
                sendToName = sendToName.partition(">")[2]
                broadcast(decodedMessage.encode(FORMAT), sendToName)
            elif message:
                broadcast(message, 'wszyscy')
        except Exception:
            # obsługa błędów
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f'\n{nickname} opuścił chat!\n'.encode(FORMAT), 'wszyscy')
            break

# odbieranie połączeń od klienta
def receive():
    while True:
        # akceptowanie nowych połączeń
        client, address = server.accept()
        print(f"Połączono - adres: {str(address)}")

        # poproszenie klienta o ustawienie nicku
        client.send("nickname".encode(FORMAT))
        nickname = client.recv(1024)
        nicknames.append(nickname)

        # dodawanie klienta do listy klientów
        clients.append(client)

        print("Nick nowego klienta: " + str(nickname.decode(FORMAT)))
        # wiadomość do wszystkich o dołączeniu nowego klienta do chatu
        broadcast(f"\n{nickname.decode(FORMAT)} dołączył do chatu!".encode(FORMAT), 'wszyscy')
        # wiadomość o pomyślnym połączeniu
        client.send("Połączono z serwerem\n".encode(FORMAT))

        # wysyłanie klientowi nieodebranych wiadomości
        for messages in messageStorage:
            if messages.encode(FORMAT) == nickname:
                print(messageStorage[nickname.decode(FORMAT)])
                broadcast(messageStorage[nickname.decode(FORMAT)], nickname.decode(FORMAT))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

# start serwera
print("Serwer wystartował...")
receive()