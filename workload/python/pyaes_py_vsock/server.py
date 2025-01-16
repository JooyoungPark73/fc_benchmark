import socket
import os

import pyaes
import base64

current_file_path = os.path.abspath(os.path.dirname(__file__))
current_folder_name = os.path.basename(current_file_path)

INPUT_FILE_NAME = "pyaes_input.txt"
OUTPUT_FILE_NAME = "pyaes_output.txt"

with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, INPUT_FILE_NAME), 'r') as f:
    INPUT_DATA = f.read()

KEY = b'\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,'
def aes_encrypt(data):
    aes = pyaes.AESModeOfOperationCTR(KEY)
    ciphertext = aes.encrypt(data)
    encoded_ciphertext = base64.b64encode(ciphertext).decode('utf-8')
    return encoded_ciphertext


def vsock_server():
    VSOCK_PORT = 50051

    # Create a vsock socket
    sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
    
    # Bind to all interfaces (CID_ANY) on the specified port
    sock.bind((socket.VMADDR_CID_ANY, VSOCK_PORT))
    
    sock.listen(1)
    print(f"Server listening on port {VSOCK_PORT}")

    while True:
        conn, _ = sock.accept()
        data = conn.recv(128)
        output = aes_encrypt(INPUT_DATA)
        conn.send(data)
        conn.close()

if __name__ == "__main__":
    vsock_server()