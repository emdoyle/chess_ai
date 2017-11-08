import tensorflow as tf
import sys
import grpc
import logging

from proto_files import predict_pb2, prediction_service_pb2, model_pb2, model_pb2_grpc
from grpc import RpcError
from grpc.beta import implementations

logger = logging.getLogger(__name__)

class PredictClient():

    def __init__(self, host, port, model_name, model_version):
        self.host = host
        self.port = port
        self.model_name = model_name
        self.model_version = model_version

    def sig_to_key(self, sig):
        if sig == 'serving_default' or sig == 'value':
            return 'value'
        if sig == 'policy':
            return sig
        return 'error'

    def predict(self, request_data, signature_name='serving_default', request_timeout=10, shape=[8*8*13]):

        logger.info('Sending request to tfserving model')
        logger.info('Model name: ' + str(self.model_name))
        logger.info('Model version: ' + str(self.model_version))
        logger.info('Host: ' + str(self.host))

        features_tensor_proto = tf.contrib.util.make_tensor_proto(request_data,
                                                                    dtype=tf.float32, shape=shape)

        # Create gRPC client and request
        channel = implementations.insecure_channel(self.host, int(self.port))
        stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
        request = predict_pb2.PredictRequest()
        request.model_spec.name = self.model_name
        request.model_spec.signature_name = signature_name

        if self.model_version > 0:
            request.model_spec.version.value = self.model_version

        request.inputs['x'].CopyFrom(features_tensor_proto)

        try:
            result = stub.Predict(request, timeout=request_timeout)
            return list(result.outputs[self.sig_to_key(signature_name)].float_val)
        except RpcError as e:
            logger.error(e)
            logger.error('Prediction failed!')