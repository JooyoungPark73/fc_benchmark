import socket
import os
from PIL import Image
import io

current_file_path = os.path.abspath(os.path.dirname(__file__))
current_folder_name = os.path.basename(current_file_path)

INPUT_FILE_NAME = "image_resize_input.jpg"
OUTPUT_FILE_NAME = "image_resize_output.jpg"

with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, INPUT_FILE_NAME), 'rb') as f:
    INPUT_DATA = f.read()


def image_resize(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        left = width / 5
        top = height / 5
        right = 4 * width / 5
        bottom = 4 * height / 5
        im1 = image.crop((left, top, right, bottom))
        
        img_byte_arr = io.BytesIO()
        im1.save(img_byte_arr, format='jpeg')
        return img_byte_arr.getvalue()
    except Exception as e:
        return f"python.image_rotate.ImageNotFound.Error:{e}".encode()



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
        output = image_resize(INPUT_DATA)
        conn.send(data)
        conn.close()

if __name__ == "__main__":
    vsock_server()