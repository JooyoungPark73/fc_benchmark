from concurrent import futures

import argparse
import grpc
import os


from io import StringIO
import pandas as pd
import sklearn.datasets as datasets
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import LinearSVR
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import roc_auc_score
import numpy as np
import pickle

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

model_config = {
    'models': [
        {
            'model': 'LinearSVR',
            'params': {
                'C': 1.0,
                'tol': 1e-6,
                'random_state': 42
            }
        },
        {
            'model': 'Lasso',
            'params': {
                'alpha': 0.1
            }
        },
        {
            'model': 'LinearRegression',
            'params': {}
        },
        {
            'model': 'RandomForestRegressor',
            'params': {
                'n_estimators': 2,
                'max_depth': 2,
                'min_samples_split': 2,
                'min_samples_leaf': 2,
                # 'n_jobs': 2,
                'random_state': 42
            }
        },
        {
            'model': 'KNeighborsRegressor',
            'params': {
                'n_neighbors': 20,
            }
        }
    ],
    'meta_model': {
        'model': 'LogisticRegression',
        'params': {}
    }
}

def model_dispatcher(model_name):
    if model_name == 'LinearSVR':
        return LinearSVR
    elif model_name == 'Lasso':
        return Lasso
    elif model_name == 'LinearRegression':
        return LinearRegression
    elif model_name == 'RandomForestRegressor':
        return RandomForestRegressor
    elif model_name == 'KNeighborsRegressor':
        return KNeighborsRegressor
    elif model_name == 'LogisticRegression':
        return LogisticRegression
    else:
        raise ValueError(f"Model {model_name} not found")

INPUT_FILE_NAME = f"dataset"
OUTPUT_MODEL_NAME = f"KNeighborsRegressor.pkl"
OUTPUT_Y_PRED_NAME = f"KNeighborsRegressor_y_pred.pkl"

def train_model(model_config, dataset):
    model_name = model_config['model']
    model_params = model_config['params']
    model = model_dispatcher(model_name)(**model_params)
    
    y_pred = cross_val_predict(model, dataset['features'], dataset['labels'], cv=5)
    model.fit(dataset['features'], dataset['labels'])
    # print(f"{model_config['model']} score: {roc_auc_score(dataset['labels'], y_pred)} {(perf_counter_ns() - time_start) // 1000000} milisec")
    return model, y_pred

class Executor(busyspin_pb2_grpc.ExecutorServicer):
    def Execute(self, request, context):
        msg = "Hello, %s!" % request.message
        rs_client = RemoteStorage("s3", current_folder_name)
        dataset, get_time = rs_client.download_file(INPUT_FILE_NAME, configs.BUCKET_NAME)
        model, y_pred = train_model(model_config['models'][4], pickle.loads(dataset))
        put_time = rs_client.upload_file(OUTPUT_MODEL_NAME, configs.BUCKET_NAME, pickle.dumps(model))
        put_time += rs_client.upload_file(OUTPUT_Y_PRED_NAME, configs.BUCKET_NAME, pickle.dumps(y_pred))
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