import socket
import os

import pandas as pd
import re

import pickle

current_file_path = os.path.abspath(os.path.dirname(__file__))
current_folder_name = os.path.basename(current_file_path)


INPUT_FILE_NAME = "lr_serving_input.txt"
INPUT_TOKENIZER_NAME = "lr_serving_tokenizer.pkl"
INPUT_SCALER_NAME = "lr_serving_scaler.pkl"
INPUT_MODEL_NAME = "lr_serving_model.pkl"
OUTPUT_FILE_NAME = "lr_serving_output.txt"

with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, INPUT_FILE_NAME), 'r') as f:
    INPUT_DATA = f.read()
with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, INPUT_TOKENIZER_NAME), 'rb') as f:
    INPUT_TOKENIZER_DATA = pickle.load(f)
with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, INPUT_SCALER_NAME), 'rb') as f:
    INPUT_SCALER_DATA = pickle.load(f)
with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, INPUT_MODEL_NAME), 'rb') as f:
    INPUT_MODEL_DATA = pickle.load(f)

cleanup_re = re.compile('[^a-z]+')

def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

def process_input(x, tfidf_vect, scaler):
    df_input = pd.DataFrame()
    df_input['x'] = [x]
    df_input['x'] = df_input['x'].apply(cleanup)
    X = tfidf_vect.transform(df_input['x'])
    X = scaler.transform(X)
    return X


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
        X = process_input(INPUT_DATA, INPUT_TOKENIZER_DATA, INPUT_SCALER_DATA)
        y = INPUT_MODEL_DATA.predict(X)
        conn.send(data)
        conn.close()

if __name__ == "__main__":
    vsock_server()