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

import pickle

INPUT_FILE_NAME = "lr_serving_input.txt"
INPUT_TOKENIZER_NAME = "lr_serving_tokenizer.pkl"
INPUT_SCALER_NAME = "lr_serving_scaler.pkl"
INPUT_MODEL_NAME = "lr_serving_model.pkl"
OUTPUT_FILE_NAME = "lr_serving_output.txt"

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

class Executor(busyspin_pb2_grpc.ExecutorServicer):
    def Execute(self, request, context):
        msg = "Hello, %s!" % request.message
        rs_client = RemoteStorage("s3", current_folder_name)
        input_bytes, get_time = rs_client.download_file(INPUT_FILE_NAME, configs.BUCKET_NAME)
        tokenizer_bytes, get_time = rs_client.download_file(INPUT_TOKENIZER_NAME, configs.BUCKET_NAME)
        scaler_bytes, get_time = rs_client.download_file(INPUT_SCALER_NAME, configs.BUCKET_NAME)
        model_bytes, get_time = rs_client.download_file(INPUT_MODEL_NAME, configs.BUCKET_NAME)
        
        X = process_input(input_bytes.decode(), pickle.loads(tokenizer_bytes), pickle.loads(scaler_bytes))
        y = pickle.loads(model_bytes).predict(X)
        put_time = rs_client.upload_file(OUTPUT_FILE_NAME, configs.BUCKET_NAME, str(y))
        
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