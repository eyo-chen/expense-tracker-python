# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from proto import stock_pb2 as proto_dot_stock__pb2

GRPC_GENERATED_VERSION = '1.71.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in proto/stock_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class StockServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Create = channel.unary_unary(
                '/stock.StockService/Create',
                request_serializer=proto_dot_stock__pb2.CreateReq.SerializeToString,
                response_deserializer=proto_dot_stock__pb2.CreateResp.FromString,
                _registered_method=True)
        self.List = channel.unary_unary(
                '/stock.StockService/List',
                request_serializer=proto_dot_stock__pb2.ListReq.SerializeToString,
                response_deserializer=proto_dot_stock__pb2.ListResp.FromString,
                _registered_method=True)
        self.GetPortfolioInfo = channel.unary_unary(
                '/stock.StockService/GetPortfolioInfo',
                request_serializer=proto_dot_stock__pb2.GetPortfolioInfoReq.SerializeToString,
                response_deserializer=proto_dot_stock__pb2.GetPortfolioInfoResp.FromString,
                _registered_method=True)
        self.GetStockInfo = channel.unary_unary(
                '/stock.StockService/GetStockInfo',
                request_serializer=proto_dot_stock__pb2.GetStockInfoReq.SerializeToString,
                response_deserializer=proto_dot_stock__pb2.GetStockInfoResp.FromString,
                _registered_method=True)


class StockServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Create(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def List(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPortfolioInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStockInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_StockServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=proto_dot_stock__pb2.CreateReq.FromString,
                    response_serializer=proto_dot_stock__pb2.CreateResp.SerializeToString,
            ),
            'List': grpc.unary_unary_rpc_method_handler(
                    servicer.List,
                    request_deserializer=proto_dot_stock__pb2.ListReq.FromString,
                    response_serializer=proto_dot_stock__pb2.ListResp.SerializeToString,
            ),
            'GetPortfolioInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetPortfolioInfo,
                    request_deserializer=proto_dot_stock__pb2.GetPortfolioInfoReq.FromString,
                    response_serializer=proto_dot_stock__pb2.GetPortfolioInfoResp.SerializeToString,
            ),
            'GetStockInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetStockInfo,
                    request_deserializer=proto_dot_stock__pb2.GetStockInfoReq.FromString,
                    response_serializer=proto_dot_stock__pb2.GetStockInfoResp.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'stock.StockService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('stock.StockService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class StockService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Create(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/stock.StockService/Create',
            proto_dot_stock__pb2.CreateReq.SerializeToString,
            proto_dot_stock__pb2.CreateResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def List(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/stock.StockService/List',
            proto_dot_stock__pb2.ListReq.SerializeToString,
            proto_dot_stock__pb2.ListResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetPortfolioInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/stock.StockService/GetPortfolioInfo',
            proto_dot_stock__pb2.GetPortfolioInfoReq.SerializeToString,
            proto_dot_stock__pb2.GetPortfolioInfoResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetStockInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/stock.StockService/GetStockInfo',
            proto_dot_stock__pb2.GetStockInfoReq.SerializeToString,
            proto_dot_stock__pb2.GetStockInfoResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
