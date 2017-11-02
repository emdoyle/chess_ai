# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import chess
import os
import numpy as np
import pandas as pd
import tensorflow as tf
import pychess_utils as util
from deepmind_mcts import MCTS

# TODO: Think of another way to encode moves?
# 8x8 choices for source square, 8x8 choices for destination square, 64^2 possible 'moves'
# this means a 64^2=4096 node output layer is required to define a full policy for a given
# position.  That could slow down training significantly...might have to revisit this
# plus 1 more target to train value per position

# Less Verbose Output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.ERROR)

class Network:

	DATA_FILE = "/Users/evanmdoyle/Programming/ChessAI/ACZData/self_play.csv"
	PIECE_PREFIXES = ['p_', 'n_', 'b_', 'r_', 'q_', 'k_']

	def __init__(self):
		self.__nn = tf.estimator.Estimator(model_fn=self.model_fn, params={})
		self.__nn.train(input_fn=self.input_fn(self.DATA_FILE, num_epochs=None, shuffle=True), steps=1)

	def feature_col_names(self):
		# 8x8 board for each piece type (6) for each player (2) plus an indicator of whose turn it is
		feature_columns = []
		for i in range(2):
			for prefix in self.PIECE_PREFIXES:
				for x in range(64):
					# Column naming convention is [color][piece prefix][square number]
					# ex: the column labeled 0p_25 holds a 1 when a black pawn occupies position 25
					feature_columns.append(str(i)+prefix+str(x))
		return feature_columns

	def target_column_names(self):
		# 'probs' here will be a string that must be decoded in model_fn
		return ['probs', 'value']

	def convert(self, uci_move):
		move = chess.Move.from_uci(uci_move)
		return (move.from_square, move.to_square)

	def decode(self, labels):
		new_labels = []
		labels = labels.split('-')
		for label in labels:
			label = label.strip('(').strip(')').split(':')
			label = (self.convert(label[0]), label[1])
			new_labels.append(label)
		return new_labels

	def create_policy(self, labels):
		policy = [float(0) for x in range(4096)]
		for moves, prob in labels:
			policy[(moves[0]*64)+moves[1]] = float(prob)
		return np.array(policy)

	def one_hot(self, value):
		if value:
			return np.array([0, 1])
		else:
			return np.array([1, 0])

	def input_fn(self, data_file, num_epochs, batch_size=30, shuffle=False, num_threads=4):
		feature_cols = self.feature_col_names()
		target_cols = self.target_column_names()
		dataset = pd.read_csv(
			tf.gfile.Open(data_file),
			header=0,
			usecols=feature_cols + target_cols,
			skipinitialspace=True,
			engine="python")
		# Drop NaN entries
		dataset.dropna(how="any", axis=0)

		# Create separate dataframe for y
		policy_labels = dataset.probs.apply(lambda x: self.create_policy(self.decode(x)))
		policy_labels = policy_labels.apply(pd.Series)

		value_labels = dataset.value.apply(lambda x: self.one_hot(x))
		value_labels = value_labels.apply(pd.Series)

		dataset.pop('probs')
		dataset.pop('value')

		return tf.estimator.inputs.numpy_input_fn(
			x={"x": np.array(dataset)},
			y=np.array(pd.concat([policy_labels, value_labels], axis=1)),
			batch_size=batch_size,
			num_epochs=num_epochs,
			shuffle=shuffle,
			num_threads=num_threads)

	def model_fn(self, features, labels, mode, params):
		# Labels need to be split into policy and value
		policy_labels, value_labels = tf.split(labels, [4096, 2], axis=1)

		# Input layer comes from features, which come from input_fn
		input_layer = tf.cast(features["x"], tf.float32)
		hidden_layer = tf.layers.dense(inputs=input_layer, units=4097, activation=None)
		policy_output_layer = tf.layers.dense(inputs=hidden_layer, units=4096, activation=None)
		value_output_layer = tf.layers.dense(inputs=hidden_layer, units=2, activation=None)
		predictions = tf.concat([policy_output_layer, value_output_layer], axis=1)
		loss = tf.add(
			tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=policy_output_layer, labels=policy_labels)),
			tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=value_output_layer, labels=value_labels))
			)
		eval_metric_ops = {}
		optimizer = tf.train.GradientDescentOptimizer(
			learning_rate=0.1)
		train_op = optimizer.minimize(
			loss=loss, global_step=tf.train.get_global_step())
		# labels = create_policy(decode(labels))
		
		return tf.estimator.EstimatorSpec(mode, predictions, loss, train_op, eval_metric_ops)
