import socket
import os

import numpy as np
import pickle

current_file_path = os.path.abspath(os.path.dirname(__file__))
current_folder_name = os.path.basename(current_file_path)

INPUT_MODEL_LIST = ["KNeighborsRegressor.pkl", "Lasso.pkl", "LinearRegression.pkl", "LinearSVR.pkl", "RandomForestRegressor.pkl"]
INPUT_Y_PRED_LIST = ["KNeighborsRegressor_y_pred.pkl", "Lasso_y_pred.pkl", "LinearRegression_y_pred.pkl", "LinearSVR_y_pred.pkl", "RandomForestRegressor_y_pred.pkl"]

OUTPUT_MODELS_DATA_NAME = "models"
OUTPUT_META_FEATURES_DATA_NAME = "meta_features"

INPUT_MODEL_DATA = []
INPUT_Y_PRED_DATA = []
for i, model_name in enumerate(INPUT_MODEL_LIST):
    with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, model_name), 'rb') as f:
        INPUT_MODEL_DATA.append(pickle.load(f))

for i, y_pred_name in enumerate(INPUT_Y_PRED_LIST):
    with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, y_pred_name), 'rb') as f:
        INPUT_Y_PRED_DATA.append(pickle.load(f))


with open(os.path.join(current_file_path, "../payload/output_payload", current_folder_name, OUTPUT_MODELS_DATA_NAME), 'rb') as f:
    OUTPUT_MODELS_DATA = pickle.load(f)
with open(os.path.join(current_file_path, "../payload/output_payload", current_folder_name, OUTPUT_META_FEATURES_DATA_NAME), 'rb') as f:
    OUTPUT_META_FEATURES_DATA = f.read()



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
        meta_features = np.transpose(np.array(INPUT_Y_PRED_DATA))
        conn.send(data)
        conn.close()

if __name__ == "__main__":
    vsock_server()