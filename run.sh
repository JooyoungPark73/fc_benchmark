# go run ./go_profiling -l python -e helloworld_vsock --loop 10 --profiling stable
# go run ./go_profiling -l python -e helloworld_vsock --loop 10 --profiling reap
# go run ./go_profiling -l python -e helloworld_tcp --loop 10 --profiling stable
# go run ./go_profiling -l python -e helloworld_tcp --loop 10 --profiling reap
# go run ./go_profiling -l python -e helloworld_grpc --loop 10 --profiling stable
# go run ./go_profiling -l python -e helloworld_grpc --loop 10 --profiling reap
# go run ./go_profiling -l python -e aes --loop 10 --profiling stable
# go run ./go_profiling -l python -e aes --loop 10 --profiling reap
# go run ./go_profiling -l python -e lr_serving --loop 10 --profiling stable
# go run ./go_profiling -l python -e lr_serving --loop 10 --profiling reap


# go run ./go_profiling -l python -e helloworld_py_grpc --loop 15 --profiling reap
# go run ./go_profiling -l python -e helloworld_py_grpc_s3 --loop 15 --profiling reap
# go run ./go_profiling -l python -e helloworld_py_vsock --loop 15 --profiling reap
# go run ./go_profiling -l python -e helloworld_py_vsock_s3 --loop 15 --profiling reap

# go run ./go_profiling -l node -e helloworld_js_grpc_s3 --loop 10 --profiling reap
# go run ./go_profiling -l node -e helloworld_js_vsock --loop 10 --profiling reap

# go run ./go_profiling -l python -e chameleon_py_grpc_s3 --loop 10 --profiling reap
# go run ./go_profiling -l python -e chameleon_py_vsock --loop 10 --profiling reap

# go run ./go_profiling -l python -e cnn_serving_py_grpc_s3 --loop 10 --profiling reap
# go run ./go_profiling -l python -e cnn_serving_py_vsock --loop 10 --profiling reap

# go run ./go_profiling -l python -e image_resize_py_grpc_s3 --loop 10 --profiling reap
# go run ./go_profiling -l python -e image_resize_py_vsock --loop 10 --profiling reap

# go run ./go_profiling -l python -e lr_serving_py_grpc_s3 --loop 10 --profiling reap
# go run ./go_profiling -l python -e lr_serving_py_vsock --loop 10 --profiling reap

# go run ./go_profiling -l python -e pyaes_py_grpc_s3 --loop 10 --profiling reap
# go run ./go_profiling -l python -e pyaes_py_vsock --loop 10 --profiling reap

# go run ./go_profiling -l python -e stack_training-reducer_py_grpc_s3 --loop 10 --profiling reap
# go run ./go_profiling -l python -e stack_training-reducer_py_vsock --loop 10 --profiling reap

# go run ./go_profiling -l python -e stack_training-trainer_py_grpc_s3 --loop 10 --profiling reap
# go run ./go_profiling -l python -e stack_training-trainer_py_vsock --loop 10 --profiling reap

# go run ./go_profiling -l python -e wordcount_py_grpc_s3 --loop 10 --profiling reap
# go run ./go_profiling -l python -e wordcount_py_vsock --loop 10 --profiling reap

go run ./go_profiling -l python -e lr_training_py_grpc_s3 --loop 10 --profiling reap
go run ./go_profiling -l python -e lr_training_py_vsock --loop 10 --profiling reap

go run ./go_profiling -l python -e image_rotate_py_grpc_s3 --loop 10 --profiling reap
go run ./go_profiling -l python -e image_rotate_py_vsock --loop 10 --profiling reap
