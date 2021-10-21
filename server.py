import sys
import os
import socket

# settings
BUFFER_SIZE = 1024
my_port = eval(sys.argv[1])
my_ip = '127.0.0.1'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((my_ip, my_port))
server.listen(1)
os.chdir(os.path.join(os.getcwd(), 'files'))

while True:
    # wait for a client
    client_socket, client_address = server.accept()
    try:
        # take a message from a client
        client_socket.settimeout(1)
        data = str(client_socket.recv(BUFFER_SIZE))
        client_socket.settimeout(None)
        # if message not done
        while data.find('\r\n\r\n') != -1:
            data += str(client_socket.recv(BUFFER_SIZE))
        # if empty question
        if data == '\r\n\r\n':
            client_socket.close()
            continue
        if not data:
            client_socket.close()
            continue

        # print data
        print(data[2:-1])
        # split data
        # path
        first_index = data.find('GET') + 5
        second_index = data.find('HTTP') - 1
        path = data[first_index:second_index]
        if path == "":
            path = 'index.html'
        # connection
        connection = ""
        if data.find('close') != -1:
            connection = 'close'
        if data.find('keep-alive') != -1:
            connection = 'keep-alive'
        # find file requested
        try:
            if path.find('redirect') != -1:
                client_socket.send(b'HTTP/1.1 301 Moved Permanently\r\n')
                client_socket.send(b'Connection: close\r\n')
                client_socket.send(b'Location: /result.html')
                client_socket.send(b'\r\n')
                client_socket.close()
                continue
            if path.find('ico') != -1 or path.find('jpg') != -1:
                # read binary file
                file = open(path, 'rb')
                content = file.read()
                message = 'HTTP/1.1 200 OK\r\n'
                message += 'Connection: ' + connection + '\r\n'
                size = len(content)
                message += 'Content-Length: ' + str(size) + '\r\n'
                message += '\r\n'
                client_socket.send(message.encode())
                client_socket.send(content)
                file.close()
            else:
                # read file
                file = open(path, 'r')
                content = file.read()
                message = 'HTTP/1.1 200 OK\r\n'
                message += 'Connection: ' + connection + '\r\n'
                size = len(content)
                message += 'Content-Length: ' + str(size) + '\r\n'
                message += '\r\n'
                message += content
                client_socket.send(message.encode())
                file.close()
        except FileNotFoundError or PermissionError:
            # wrong path
            client_socket.send(b'HTTP/1.1 404 Not Found\r\n')
            client_socket.send(b'Connection: close\r\n')
            client_socket.send(b'\r\n')
            client_socket.close()
            continue
        if connection == 'close':
            client_socket.close()
            continue
    except socket.timeout:
        client_socket.close()
        continue
