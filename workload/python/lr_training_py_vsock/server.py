import socket
import os

import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from io import StringIO


import pickle

current_file_path = os.path.abspath(os.path.dirname(__file__))
current_folder_name = os.path.basename(current_file_path)

cleanup_re = re.compile('[^a-z]+')

def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

INPUT_FILE_NAME = "lr_training_input.csv"
OUTPUT_TOKENIZER_NAME = "lr_training_tokenizer.pkl"
OUTPUT_SCALER_NAME = "lr_training_scaler.pkl"
OUTPUT_MODEL_NAME = "lr_training_model.pkl"

with open(os.path.join(current_file_path, "../payload/input_payload", "lr_training", INPUT_FILE_NAME), 'r') as f:
    INPUT_DATA = f.read()


def prepare_data(byte_stream):
    string_data = StringIO(byte_stream.decode('utf-8'))
    data = pd.read_csv(string_data)
    data['train'] = data['Text'].apply(cleanup)
    return data

def model_train(df):
    # Increase max_iter and add other parameters for better convergence
    model = LogisticRegression(
        max_iter=500,  # Increased from 10 to 4000
        C=1.0,         # Add regularization parameter
        solver='lbfgs'  # Explicitly specify solver
    )
    
    # Modify TfidfVectorizer parameters
    tfidf_vector = TfidfVectorizer(
        min_df=100,    # Reduced from 1000 to avoid too sparse features
        max_features=10000  # Limit number of features
    ).fit(df['train'])
    
    # Transform the data
    train = tfidf_vector.transform(df['train'])
    
    # Add scaling for sparse matrices
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler(with_mean=False)  # with_mean=False for sparse matrices
    train_scaled = scaler.fit_transform(train)
    
    # Fit the model with scaled data
    model.fit(train_scaled, df['Score'])
    
    # Save tokenizer, scaler, and model
    return tfidf_vector, scaler, model


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
        dataset = pd.read_csv(StringIO(INPUT_DATA))
        dataset['train'] = dataset['Text'].apply(cleanup)
        SAMPLE_DATASET = dataset
        data = prepare_data(SAMPLE_DATASET)
        tokenizer, scaler, model = model_train(data)
        conn.send(data)
        conn.close()

if __name__ == "__main__":
    vsock_server()