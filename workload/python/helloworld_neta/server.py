from concurrent import futures

import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

from neta import S3Neta


class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        neta = S3Neta(2, 52)
        buf = neta.get_object("nexus-benchmark-payload", "input_payload/auth/auth_input.txt")
        print(f"{len(buf)} bytes received")
        
        temp = neta.put_object("nexus-benchmark-payload", "output_payload/auth/auth_output.txt", buf)
        print(f"Operation result: {temp}")
        
        msg = f"fn: Example | input: auth_input.txt | return msg: auth_output.txt | runtime: Python"
        return helloworld_pb2.HelloReply(message=msg)
    

def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
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