import socket
import boto3

def vsock_server():
    VSOCK_PORT = 50051

    # Create a vsock socket
    sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
    
    # Bind to all interfaces (CID_ANY) on the specified port
    sock.bind((socket.VMADDR_CID_ANY, VSOCK_PORT))
    
    sock.listen(1)
    print(f"Server listening on port {VSOCK_PORT}")

    while True:
        conn, (cid, port) = sock.accept()
        print(f"Connection from CID: {cid}, Port: {port}")

        # Receive data from the client
        data = conn.recv(1024).decode()
        print(f"Received: {data}")

        # Send a response
        msg = f"Hello from guest! You said: {data}"
        
        s3_client = boto3.client('s3')
        try:
            response = s3_client.get_object(Bucket='nexus-benchmark-payload', Key='input_payload/auth/auth_input.txt')
            response = response['Body'].read()
        except Exception as e:
            print(f"Error: {e}")
            msg = "Error"
        
        try:
            response = s3_client.put_object(Bucket='nexus-benchmark-payload', Key='output_payload/auth/auth_output.txt', Body=response)
        except Exception as e:
            print(f"Error: {e}")
            msg = "Error"
        
        conn.send(msg.encode())

        conn.close()

if __name__ == "__main__":
    vsock_server()