from concurrent import futures

import argparse
import grpc
import os

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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from io import StringIO
import pickle

cleanup_re = re.compile('[^a-z]+')

def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

REMOTE_STORAGE_TYPE = os.getenv("REMOTE_STORAGE_TYPE", "minio")
PREPARE_DATA = os.getenv("PREPARE_DATA", "true")

INPUT_FILE_NAME = "lr_training_input.csv"
OUTPUT_TOKENIZER_NAME = "lr_training_tokenizer.pkl"
OUTPUT_SCALER_NAME = "lr_training_scaler.pkl"
OUTPUT_MODEL_NAME = "lr_training_model.pkl"

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

class Executor(busyspin_pb2_grpc.ExecutorServicer):
    def Execute(self, request, context):
        msg = "Hello, %s!" % request.message
        rs_client = RemoteStorage("s3", "lr_training")
        input_bytes, get_time = rs_client.download_file(INPUT_FILE_NAME, configs.BUCKET_NAME)
        data = prepare_data(input_bytes)
        tokenizer, scaler, model = model_train(data)
        put_time = rs_client.upload_file(OUTPUT_TOKENIZER_NAME, configs.BUCKET_NAME, pickle.dumps(tokenizer))
        put_time += rs_client.upload_file(OUTPUT_SCALER_NAME, configs.BUCKET_NAME, pickle.dumps(scaler))
        put_time += rs_client.upload_file(OUTPUT_MODEL_NAME, configs.BUCKET_NAME, pickle.dumps(model))
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