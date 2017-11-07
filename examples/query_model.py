# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import chess
import numpy as np
import tensorflow as tf
import pychess_utils as util
from rpc_client import PredictClient

client = PredictClient('127.0.0.1', 9000, 'default', 1509741473)
print(client.predict(util.expand_position(chess.Board())))
print(client.predict(util.expand_position(chess.Board()), 'policy'))