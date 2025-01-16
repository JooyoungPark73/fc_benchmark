package main

import (
	"fmt"

	"golang.org/x/sys/unix"
)

const (
	AF_VSOCK       = 40
	VMADDR_CID_ANY = 0xffffffff
)

func main() {
	vsockPort := uint32(50051)

	// Create vsock socket
	fd, err := unix.Socket(AF_VSOCK, unix.SOCK_STREAM, 0)
	if err != nil {
		fmt.Printf("Failed to create socket: %v\n", err)
		return
	}
	defer unix.Close(fd)

	// Bind socket
	sa := &unix.SockaddrVM{
		CID:  VMADDR_CID_ANY,
		Port: vsockPort,
	}
	if err := unix.Bind(fd, sa); err != nil {
		fmt.Printf("Failed to bind: %v\n", err)
		return
	}

	// Listen for connections
	if err := unix.Listen(fd, 1); err != nil {
		fmt.Printf("Failed to listen: %v\n", err)
		return
	}

	fmt.Printf("Server listening on port %d\n", vsockPort)

	for {
		// Accept connection
		connFd, _, err := unix.Accept(fd)
		if err != nil {
			fmt.Printf("Failed to accept: %v\n", err)
			continue
		}

		// Read data
		buf := make([]byte, 128)
		n, err := unix.Read(connFd, buf)
		if err != nil {
			fmt.Printf("Failed to read: %v\n", err)
			unix.Close(connFd)
			continue
		}

		// Echo data back
		if _, err := unix.Write(connFd, buf[:n]); err != nil {
			fmt.Printf("Failed to write: %v\n", err)
		}

		// Close connection
		unix.Close(connFd)
	}
}
