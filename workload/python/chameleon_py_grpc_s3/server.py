from concurrent import futures

import argparse
import grpc
import os

import six
from chameleon import PageTemplate

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

INPUT_FILE_NAME = "chameleon_input.txt"
OUTPUT_FILE_NAME = "chameleon_output.html"

BIGTABLE_ZPT = """\
<table xmlns="http://www.w3.org/1999/xhtml"
xmlns:tal="http://xml.zope.org/namespaces/tal">
<tr tal:repeat="row python: options['table']">
<td tal:repeat="c python: row.values()">
<span tal:define="d python: c + 1"
tal:attributes="class python: 'column-' + %s(d)"
tal:content="python: d" />
</td>
</tr>
</table>""" % six.text_type.__name__

template = PageTemplate(BIGTABLE_ZPT)

def cameleon(num_of_cols, num_of_rows):
    data = {}
    for i in range(num_of_cols):
        data[str(i)] = i
    
    table = [data for x in range(num_of_rows)]
    options = {'table': table}

    data = template.render(options=options)

    return data


class Executor(busyspin_pb2_grpc.ExecutorServicer):
    def Execute(self, request, context):
        msg = "Hello, %s!" % request.message
        rs_client = RemoteStorage("s3", current_folder_name)
        input_bytes, get_time = rs_client.download_file(INPUT_FILE_NAME, configs.BUCKET_NAME)
        render_col = int(input_bytes.decode().split('\n')[0])
        render_row = int(input_bytes.decode().split('\n')[1])
        output = cameleon(render_col, render_row)
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