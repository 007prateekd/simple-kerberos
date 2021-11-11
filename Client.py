import socket
from cryptography.fernet import Fernet
import time

user   = "Alice"
server = "Bob"
key_AS = b"UFltX3Uf9qIQ6UyIElj3awsXWDHsC2QjZ8GObFMqzmQ="

## COMM. WITH KDC
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port_KDC, port_server = 11111, 22222
client.connect(("127.0.0.1", port_KDC))
# Step 1
client.send(user.encode())
enc = client.recv(1024)
print("Sending connection request to Authentication Server...")

# Step 2
fernet_1 = Fernet(key_AS)
(key_TGS, enc_2) = fernet_1.decrypt(enc).decode().split()
print("Ticket received from Authentication Server")
print(f"Ticket: {key_TGS}")
# Step 3
fernet_2 = Fernet(key_TGS)
nonce = int(time.time())
enc_1 = fernet_2.encrypt((server + ' ' + str(nonce)).encode())
enc = enc_1.decode() + ' ' + enc_2
client.send(enc.encode())
print(f"Sending Nonce: {nonce} to Ticket Granting Server...")
# Step 4
(enc_1, enc_2) = client.recv(1024).decode().split()
(server_tmp, key_session) = fernet_2.decrypt(enc_1.encode()).decode().split()
client.close()
print("Session Key received from Ticket Granting Server")
print(f"Session Key: {key_session}")
print()

## COMM. WITH SERVER
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", port_server))
# Step 5
print(f"Sending Nonce: {nonce} and Session Key to Server: {server}...")
fernet_3 = Fernet(key_session.encode())
enc_1 = fernet_3.encrypt(str(nonce).encode())
enc = enc_1.decode() + ' ' + enc_2
client.send(enc.encode())
# Step 6
enc = client.recv(1024)
nonce_new = fernet_3.decrypt(enc).decode()
print(f"New Nonce: {nonce_new} received from Server: {server}")
print(f"Connection Established Successfully")
client.close()
