const net = require('net');

function vsockClient() {
    const VSOCK_PATH = "/tmp/v.sock";
    const GUEST_CID = 2;
    const VSOCK_PORT = 50051;

    // Create Unix domain socket connection
    const client = new net.Socket();

    client.connect(VSOCK_PATH, () => {
        console.log('Connected to Firecracker vsock');
        
        // Send CONNECT command
        client.write(`CONNECT ${VSOCK_PORT}\n`);
    });

    client.on('data', (data) => {
        const response = data.toString().trim();
        
        if (response.startsWith('OK')) {
            console.log('vsock connection established');
            
            // Send message after connection is established
            const message = 'Hello from host!';
            client.write(message);
        } else {
            console.log(`Received from guest: ${response}`);
            client.end(); // Close the connection after receiving response
        }
    });

    client.on('error', (err) => {
        console.error('Connection error:', err);
    });

    client.on('close', () => {
        console.log('Connection closed');
    });
}

vsockClient();
