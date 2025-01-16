from concurrent import futures

import argparse
import grpc
import os

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


INPUT_MODEL_LIST = ["KNeighborsRegressor.pkl", "Lasso.pkl", "LinearRegression.pkl", "LinearSVR.pkl", "RandomForestRegressor.pkl"]
INPUT_Y_PRED_LIST = ["KNeighborsRegressor_y_pred.pkl", "Lasso_y_pred.pkl", "LinearRegression_y_pred.pkl", "LinearSVR_y_pred.pkl", "RandomForestRegressor_y_pred.pkl"]

OUTPUT_MODELS_DATA_NAME = "models"
OUTPUT_META_FEATURES_DATA_NAME = "meta_features"

class Executor(busyspin_pb2_grpc.ExecutorServicer):
    def Execute(self, request, context):
        msg = "Hello, %s!" % request.message
        rs_client = RemoteStorage("s3", current_folder_name)
        models = []
        y_preds = []
        for i, model_name in enumerate(INPUT_MODEL_LIST):
            model, get_time = rs_client.download_file(model_name, configs.BUCKET_NAME)
            models.append(pickle.loads(model))
            
        for i, y_pred_name in enumerate(INPUT_Y_PRED_LIST):
            y_pred, get_time = rs_client.download_file(y_pred_name, configs.BUCKET_NAME)
            y_preds.append(pickle.loads(y_pred))
        
        meta_features = np.transpose(np.array(y_preds))
        
        put_time = rs_client.upload_file(OUTPUT_MODELS_DATA_NAME, configs.BUCKET_NAME, pickle.dumps(models))
        put_time += rs_client.upload_file(OUTPUT_META_FEATURES_DATA_NAME, configs.BUCKET_NAME, pickle.dumps(meta_features))
    
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