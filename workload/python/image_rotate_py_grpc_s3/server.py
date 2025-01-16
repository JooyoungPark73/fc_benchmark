from concurrent import futures

import argparse
import grpc
import os

from PIL import Image
import io

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

INPUT_FILE_NAME = "image_mod_input.jpg"
OUTPUT_FILE_NAME = "image_rotate_output.jpg"

def image_rotate_function(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.transpose(Image.ROTATE_90)

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='jpeg')
        return img_byte_arr.getvalue()
    except Exception as e:
        return f"python.image_rotate.ImageNotFound.Error:{e}".encode()

class Executor(busyspin_pb2_grpc.ExecutorServicer):
    def Execute(self, request, context):
        msg = "Hello, %s!" % request.message
        rs_client = RemoteStorage("s3", "image_mod")
        input_bytes, get_time = rs_client.download_file(INPUT_FILE_NAME, configs.BUCKET_NAME)
        output = image_rotate_function(input_bytes)
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