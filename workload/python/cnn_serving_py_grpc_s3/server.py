from concurrent import futures

import argparse
import grpc
import os

import tempfile
import torch
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights
from PIL import Image


current_file_path = os.path.abspath(os.path.dirname(__file__))
current_folder_name = os.path.basename(current_file_path)
grpc_path = os.path.join(current_file_path, "../proto")
os.sys.path.append(grpc_path)
import busyspin_pb2
import busyspin_pb2_grpc

remote_storage_path = os.path.join(current_file_path, "../utils")
os.sys.path.append(remote_storage_path)
from remote_storage import RemoteStorage
import configs

import pandas as pd
import re

import pickle

INPUT_FILE_NAME = "cnn_input.jpg"
OUTPUT_FILE_NAME = "cnn_output.txt"

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


class Executor(busyspin_pb2_grpc.ExecutorServicer):
    def Execute(self, request, context):
        msg = "Hello, %s!" % request.message
        rs_client = RemoteStorage("s3", current_folder_name)
        input_bytes, get_time = rs_client.download_file(INPUT_FILE_NAME, configs.BUCKET_NAME)
        output = cnn_serving(input_bytes)
        put_time = rs_client.upload_file(OUTPUT_FILE_NAME, configs.BUCKET_NAME, output)
        
        resp = busyspin_pb2.FaasReply(
            message=msg, 
            durationInMicroSec = 0,
            memoryUsageInKb = 0,
            ioTimeInMicroSec = 0, 
            )
        return resp


def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    busyspin_pb2_grpc.add_ExecutorServicer_to_server(Executor(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC client for image rotation')
    parser.add_argument('-a', '--addr', type=str, default="192.168.0.2", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()
    
    serve(args.addr, args.port)