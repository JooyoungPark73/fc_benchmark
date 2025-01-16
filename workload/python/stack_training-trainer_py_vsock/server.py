import socket
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

with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, INPUT_FILE_NAME), 'rb') as f:
    INPUT_DATA = pickle.load(f)
        

def train_model(model_config, dataset):
    model_name = model_config['model']
    model_params = model_config['params']
    model = model_dispatcher(model_name)(**model_params)
    
    y_pred = cross_val_predict(model, dataset['features'], dataset['labels'], cv=5)
    model.fit(dataset['features'], dataset['labels'])
    # print(f"{model_config['model']} score: {roc_auc_score(dataset['labels'], y_pred)} {(perf_counter_ns() - time_start) // 1000000} milisec")
    return model, y_pred


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
        model, y_pred = train_model(model_config['models'][4], INPUT_DATA)
        conn.send(data)
        conn.close()

if __name__ == "__main__":
    vsock_server()