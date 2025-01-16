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

import boto3


class Executor(busyspin_pb2_grpc.ExecutorServicer):
    def Execute(self, request, context):
        msg = "Hello, %s!" % request.message
        s3_client = boto3.client('s3')
        try:
            response = s3_client.get_object(Bucket='nexus-benchmark-payload', Key='input_payload/auth/auth_input.txt')
            response = response['Body'].read()
        except Exception as e:
            print(f"Error: {e}")
            msg = "Error"
            resp = busyspin_pb2.FaasReply(
                message=msg, 
                durationInMicroSec = 0,
                memoryUsageInKb = 0,
                ioTimeInMicroSec = 0, 
                )
            return resp
        
        try:
            response = s3_client.put_object(Bucket='nexus-benchmark-payload', Key='output_payload/auth/auth_output.txt', Body=response)
        except Exception as e:
            print(f"Error: {e}")
            msg = "Error"
            resp = busyspin_pb2.FaasReply(
                message=msg, 
                durationInMicroSec = 0,
                memoryUsageInKb = 0,
                ioTimeInMicroSec = 0, 
                )
            return resp
        
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