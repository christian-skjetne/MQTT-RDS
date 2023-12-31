import socket

HOST = "10.0.10.100"  # The server's hostname or IP address
PORT = 5555  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"*DPS1\n\r")
    data = s.recv(1024)

print(f"Received {data!r}")