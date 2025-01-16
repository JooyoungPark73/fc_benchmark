const { VsockServer, VsockSocket } = require('node-vsock');

function vsockServer() {
    const VSOCK_PORT = 50051;
    
    // Create a vsock server
    const server = new VsockServer();
    
    // Handle server errors
    server.on('error', (err) => {
        console.error("Server error:", err);
    });
    
    // Handle incoming connections
    server.on('connection', (socket) => {
        console.log("New socket connection...");
        
        // Handle socket errors
        socket.on('error', (err) => {
            console.error("Socket error:", err);
        });
        
        // Handle incoming data
        socket.on('data', (buf) => {
            // Echo back the received data
            socket.writeTextSync(buf.toString());
        });
        
        // Optional: Handle socket close
        socket.on('close', () => {
            console.log("Socket closed");
        });
    });
    
    // Start listening
    server.listen(VSOCK_PORT);
    console.log(`Server listening on port ${VSOCK_PORT}`);
}

// Start the server
vsockServer();
