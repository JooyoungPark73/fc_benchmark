package main

import (
	"bytes"
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"net"

	pb "github.com/JooyoungPark73/network-deputy/pkg/proto/workload"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"google.golang.org/grpc"
)

type server struct {
	pb.UnimplementedExecutorServer
}

func (s *server) Execute(ctx context.Context, req *pb.FaasRequest) (*pb.FaasReply, error) {
	msg := fmt.Sprintf("Hello, %s!", req.Message)

	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Printf("Error loading AWS config: %v", err)
		return &pb.FaasReply{
			Message:            "Error",
			DurationInMicroSec: 0,
			MemoryUsageInKb:    0,
			IoTimeInMicroSec:   0,
		}, nil
	}

	s3Client := s3.NewFromConfig(cfg)

	// Get object from S3
	getInput := &s3.GetObjectInput{
		Bucket: aws.String("nexus-benchmark-payload"),
		Key:    aws.String("input_payload/auth/auth_input.txt"),
	}

	result, err := s3Client.GetObject(ctx, getInput)
	if err != nil {
		log.Printf("Error getting object from S3: %v", err)
		return &pb.FaasReply{
			Message:            "Error",
			DurationInMicroSec: 0,
			MemoryUsageInKb:    0,
			IoTimeInMicroSec:   0,
		}, nil
	}

	body, err := io.ReadAll(result.Body)
	if err != nil {
		log.Printf("Error reading response body: %v", err)
		return &pb.FaasReply{
			Message:            "Error",
			DurationInMicroSec: 0,
			MemoryUsageInKb:    0,
			IoTimeInMicroSec:   0,
		}, nil
	}
	defer result.Body.Close()

	// Put object to S3
	putInput := &s3.PutObjectInput{
		Bucket: aws.String("nexus-benchmark-payload"),
		Key:    aws.String("output_payload/auth/auth_output.txt"),
		Body:   bytes.NewReader(body),
	}

	_, err = s3Client.PutObject(ctx, putInput)
	if err != nil {
		log.Printf("Error putting object to S3: %v", err)
		return &pb.FaasReply{
			Message:            "Error",
			DurationInMicroSec: 0,
			MemoryUsageInKb:    0,
			IoTimeInMicroSec:   0,
		}, nil
	}

	return &pb.FaasReply{
		Message:            msg,
		DurationInMicroSec: 0,
		MemoryUsageInKb:    0,
		IoTimeInMicroSec:   0,
	}, nil
}

func main() {
	addr := flag.String("addr", "192.168.0.2", "Server IP address")
	port := flag.String("port", "50051", "Server port number")
	flag.Parse()

	lis, err := net.Listen("tcp", fmt.Sprintf("%s:%s", *addr, *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterExecutorServer(s, &server{})

	log.Printf("Server started, listening on %s", *port)
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
