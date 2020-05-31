import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5200  # The port used by the server


def main():

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        addr = (HOST, 5211)
        s.sendto(b'Packet\nLabas\ntomas_pc|0|self\ntomas_pc|0|self'
                 b'\ntomas_pc|0'
                 b'|self\ntomasdpc|0|self\ntomasdpc|0|self\ntomas_pc|0|self\n'
                 b'', addr)

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((HOST, PORT))
            while True:
                message, address = s.recvfrom(1024)
                print('Received', message)


if __name__ == "__main__":
    main()
