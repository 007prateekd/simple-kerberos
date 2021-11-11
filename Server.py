import socket
from cryptography.fernet import Fernet

user   = "Alice"
server = "Bob"
key_TGS = b"BgIFUaxnefMzR1FI_Sv-meLxCV4e5RI6zp-5Y_RlR6s="

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
port = 22222          
server_socket.bind(("127.0.0.1", port))        
server_socket.listen(5)    

while True:
    # Step 5
    c, addr = server_socket.accept()    
    (enc_1, enc_2) = c.recv(1024).decode().split()
    print(f"Connection request received from Client: {user}, Address: {addr}")
    # Step 6
    fernet_1 = Fernet(key_TGS)
    (user_tmp, key_session) = fernet_1.decrypt(enc_2.encode()).split()
    fernet_2 = Fernet(key_session)
    nonce = fernet_2.decrypt(enc_1.encode()).decode()
    nonce_new = str(int(nonce) - 1)
    enc = fernet_2.encrypt(nonce_new.encode())
    c.send(enc)
    print(f"Nonce: {nonce} received from Client: {user_tmp}")
    print(f"Session Key: {key_session} received from Client: {user_tmp}")
    print(f"Sending new Nonce: {nonce_new} to Client: {user_tmp}...")
    c.close()
    break
