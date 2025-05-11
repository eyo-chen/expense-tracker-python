#!/bin/bash

set -x

protoc --version

# Generate Python Protobuf and gRPC code using grpcio-tools
python -m grpc_tools.protoc -I /proto \
    --python_out=/proto \
    --grpc_python_out=/proto \
    /proto/stock.proto