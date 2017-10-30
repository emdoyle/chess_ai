# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import chess
import os
import numpy as np
import pandas as pd
import tensorflow as tf
import pychess_utils as util
from tensorflow.contrib.learn.python.learn.datasets import base

# Less Verbose Output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.ERROR)

DATA_DIR = "/Users/evanmdoyle/Programming/ChessAI/DerivedData/complete/full_dataset/csv"
