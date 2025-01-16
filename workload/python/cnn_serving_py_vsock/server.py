import socket
import os

import tempfile
import torch
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights
from PIL import Image

current_file_path = os.path.abspath(os.path.dirname(__file__))
current_folder_name = os.path.basename(current_file_path)


INPUT_FILE_NAME = "cnn_input.jpg"
OUTPUT_FILE_NAME = "cnn_output.txt"

with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, INPUT_FILE_NAME), 'rb') as f:
    INPUT_DATA = f.read()


model = mobilenet_v3_large(weights=MobileNet_V3_Large_Weights.DEFAULT)
model.eval()

# Download ImageNet labels
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
import urllib.request
lblPath = "/tmp/imagenet_classes.txt"
urllib.request.urlretrieve(LABELS_URL, lblPath)

with open(lblPath, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Define image transformation pipeline
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def cnn_serving(image_bytes):
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(image_bytes)
            temp_file_path = temp_file.name
        
        # Load and preprocess the image
        img = Image.open(temp_file_path).convert('RGB')
        img_tensor = transform(img)
        img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
        
        # Inference
        with torch.no_grad():
            output = model(img_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
        # Get top 5 predictions
        top5_prob, top5_idx = torch.topk(probabilities, 5)
        
        # Format results
        inference = ''
        for prob, idx in zip(top5_prob, top5_idx):
            inference += f'With prob = {prob:.5f}, it contains {labels[idx]}. '
            
        return inference
    
    except Exception as e:
        return f"python.image_processing.ImageProcessingError:{e}".encode()
        
    finally:
        os.unlink(temp_file_path)



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
        output = cnn_serving(INPUT_DATA)
        conn.send(data)
        conn.close()

if __name__ == "__main__":
    vsock_server()