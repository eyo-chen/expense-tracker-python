#!/bin/bash

set -x

protoc --version

# Generate Python Protobuf and gRPC code using grpcio-tools
python -m grpc_tools.protoc -Iproto=src/proto \
    --python_out=src/ \
    --grpc_python_out=src/ \
    src/proto/stock.proto