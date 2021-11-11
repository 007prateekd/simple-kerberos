import socket
from cryptography.fernet import Fernet

key_AS = {}
key_TGS = {}
key_AS_TGS      = b"nrpuhqpzDIPzn_QxHIOE4LpZNHi5AP8lRy_wfCTqN4s="
key_AS["Alice"] = b"UFltX3Uf9qIQ6UyIElj3awsXWDHsC2QjZ8GObFMqzmQ=" 
key_TGS["Bob"]  = b"BgIFUaxnefMzR1FI_Sv-meLxCV4e5RI6zp-5Y_RlR6s="

kdc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
kdc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
port = 11111          
kdc.bind(("127.0.0.1", port))        
kdc.listen(5)    

while True:
    # Step 1
    c, addr = kdc.accept()  
    user = c.recv(1024).decode()
    print(f"Connection request received from Client: {user}, Address: {addr}")
    # Step 2
    key_TGS[user] = Fernet.generate_key()
    fernet_1 = Fernet(key_AS_TGS)
    inner = fernet_1.encrypt((user + ' ' + key_TGS[user].decode()).encode())
    fernet_2 = Fernet(key_AS[user])
    outer = fernet_2.encrypt((key_TGS[user].decode() + ' ' + inner.decode()).encode())
    c.send(outer)
    print(f"Sending Ticket: {key_TGS[user]} to Client: {user}...")
    # Step 3
    (enc_1, enc_2) = c.recv(1024).decode().split()
    print("Nonce received")
    # Step 4
    key_session = Fernet.generate_key()
    fernet_3 = Fernet(key_TGS[user])
    (server, nonce) = fernet_3.decrypt(enc_1.encode()).decode().split()
    fernet_4 = Fernet(key_TGS[server])
    (user, key_tmp) = fernet_1.decrypt(enc_2.encode()).decode().split() 
    enc_1 = fernet_3.encrypt((server + ' ' + key_session.decode()).encode())
    enc_2 = fernet_4.encrypt((user   + ' ' + key_session.decode()).encode())
    enc = (enc_1.decode() + ' ' + enc_2.decode()).encode()
    c.send(enc)
    print(f"Sending Session Key: {key_session} to Client: {user}...")
    c.close()
    break
