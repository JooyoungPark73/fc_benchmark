import socket
import os

current_file_path = os.path.abspath(os.path.dirname(__file__))
current_folder_name = os.path.basename(current_file_path)

INPUT_FILE_NAME = "chameleon_input.txt"
OUTPUT_FILE_NAME = "chameleon_output.html"

with open(os.path.join(current_file_path, "../payload/input_payload", current_folder_name, INPUT_FILE_NAME), 'r') as f:
        INPUT_DATA = f.read()


render_col = int(INPUT_DATA.split('\n')[0])
render_row = int(INPUT_DATA.split('\n')[1])

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
        global render_col, render_row
        output = cameleon(render_col, render_row)
        conn.send(data)
        conn.close()

if __name__ == "__main__":
    vsock_server()