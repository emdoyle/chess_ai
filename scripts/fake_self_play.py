# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import random
import chess
import pychess_utils as util
DST_FILE = "ACZData/self_play.csv"
PIECE_PREFIXES = ['p_', 'n_', 'b_', 'r_', 'q_', 'k_']

def feature_col_names():
	# 8x8 board for each piece type (6) for each player (2) plus an indicator of whose turn it is
	feature_columns = []
	for i in range(2):
		for prefix in PIECE_PREFIXES:
			for x in range(64):
				# Column naming convention is [color][piece prefix][square number]
				# ex: the column labeled 0p_25 holds a 1 when a black pawn occupies position 25
				feature_columns.append(str(i)+prefix+str(x))
	for x in range(64):
		feature_columns.append('turn'+str(x))
	return feature_columns

def target_column_names():
	# 'probs' here will be a string that must be decoded in model_fn
	return ['probs', 'value']

with open(DST_FILE, 'w') as f:
	for name in (feature_col_names() + target_column_names()):
		f.write(name)
		if name != 'value':
			f.write(',')
	f.write("\n")
	turn = True
	board = chess.Board()
	for i in range(500):
		turn = not turn
		for name in (feature_col_names() + target_column_names()):
			if name != 'probs' and 'turn' not in name:
				f.write(str(random.randint(0,1)))
			elif 'turn' in name:
				f.write(str(int(turn)))
			else:
				rand_move = random.choice(list(board.legal_moves))
				prob = random.uniform(0,1)
				f.write("({}:{})".format(
					util.get_prediction_index(rand_move),
					prob))
				board.push(rand_move)

			if name != 'value':
				f.write(',')
		f.write("\n")


def write_header():
	with open(DST_FILE, 'w') as f:
		for name in (feature_col_names() + target_column_names()):
			f.write(name)
			if name != 'value':
				f.write(',')
		f.write("\n")