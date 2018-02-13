import chess
import math
import numpy as np
from os import listdir

EXPORT_DIR = "/Users/evanmdoyle/Programming/ChessAI/Export/"
BEST_VERSION = "/Users/evanmdoyle/Programming/ChessAI/best_version"

def decode_result(result, turn):
	if result == '1-0':
		return float(turn)
	if result == '0-1':
		return float(not turn)
	if result == '1/2-1/2':
		return 0.5
	return None

def decode_symbol(symbol):
	symbols = ['p', 'n', 'b', 'r', 'q', 'k',
		'P', 'N', 'B', 'R', 'Q', 'K']
	return symbols.index(symbol)

def num_squares_attacking(square, board):
	return len(board.attacks(square))

def build_def_heatmap(board):
	heatmap = [0 for k in range(64)]
	for square in chess.SQUARES:
		piece = board.piece_at(square)
		if piece is not None:
			color = piece.color
			num_attackers = len(board.attackers(not color, square))
			heatmap[square] = (num_attackers if color else -num_attackers)
	return heatmap

def build_off_heatmap(board):
	heatmap = [0 for k in range(64)]
	for square in chess.SQUARES:
		piece = board.piece_at(square)
		if piece is not None:
			color = piece.color
			for a_square in board.attacks(square):
				heatmap[a_square] += (1 if color else -1)
	return heatmap

def print_heatmap(heatmap):
	for row in list(reversed(np.reshape(np.array(heatmap), (8,8)))):
		 print(row)

def expand_position(position):
	expanded = [0 for i in range(64*13)]

	if type(position) != chess.Board:
		print("Tried to expand non-Board object")
		return []

	for square in chess.SQUARES:
		piece = position.piece_at(square)
		if piece:
			offset = decode_symbol(piece.symbol())
			expanded[(offset*64)+square] = 1
	if position.turn:
		expanded[(12*64):] = [1]*64

	return expanded

def dir_and_dist(square1, square2):
	rank1 = chess.square_rank(square1)
	rank2 = chess.square_rank(square2)
	file1 = chess.square_file(square1)
	file2 = chess.square_file(square2)

	horiz = 'W' if file1 > file2 else 'E'
	vert = 'S' if rank1 > rank2 else 'N'

	filedist = abs(file1 - file2)
	rankdist = abs(rank1 - rank2)
	diag = filedist == rankdist
	straight = filedist == 0 or rankdist == 0
	knight = (filedist == 1 and rankdist == 2) or (filedist == 2 and rankdist == 1)
	far = 'F' if rankdist == 2 else 'S'

	if diag:
		dist = filedist
		return {'dir': '{}{}'.format(vert, horiz), 'dist': dist}
	elif straight:
		queen_dir = horiz if filedist != 0 else vert
		dist = filedist if filedist != 0 else rankdist
		return {'dir': '{}'.format(queen_dir), 'dist': dist}
	elif knight:
		# The distance should not be needed when handling a knight move, -1 is an indicator
		return {'dir': '{}{}{}'.format(vert, horiz, far), 'dist': -1}


# Move Encoding (as described in AlphaZero paper):
#	8x8x73 output layer
#	8x8 = square from which to 'pick up' a piece
#	56 = 'queen moves' for the piece {N, NE, E, SE, S, SW, W, NW} x {maximum 7 squares} = 56
#	8 = 'knight moves' for the piece
#	9 = underpromotions {N, B, R} x {left diag, forward, right diag}
# plus 1 more target to train value per position
def get_prediction_index(move):
	num_queen_moves = 56
	num_knight_moves = 8
	queen_map = {
		'N': 0,
		'NE': 1,
		'E': 2,
		'SE': 3,
		'S': 4,
		'SW': 5,
		'W': 6,
		'NW': 7
	}
	knight_map = {
		'NWF': 0,
		'NWS': 1,
		'NEF': 2,
		'NES': 3,
		'SEF': 4,
		'SES': 5,
		'SWF': 6,
		'SWS': 7
	}
	# there are 73 entries for each from_square
	from_index = move.from_square*73
	dir_dist = dir_and_dist(move.from_square, move.to_square)
	direction = dir_dist['dir']
	distance = dir_dist['dist']

	if distance == -1:
		offset = num_queen_moves + knight_map[direction]
	elif move.promotion:
		left = direction == 'NW' or direction == 'SE'
		right = direction == 'NE' or direction == 'SW'
		straight = direction == 'N' or direction == 'S'

		# move.promotion maps 5: Q, 4: R, 3: B, 2: N
		if left:
			offset = num_queen_moves + num_knight_moves + (move.promotion-2)*3
		elif right:
			offset = num_queen_moves + num_knight_moves + (move.promotion-2)*3 + 1
		elif straight:
			offset = num_queen_moves + num_knight_moves + (move.promotion-2)*3 + 2
	else:
		offset = queen_map[direction]*7 + distance

	return from_index + offset

def best_version():
	with open(BEST_VERSION, 'r') as f:
		return int(f.read())

def update_best_player(version):
	if type(version) != int:
		print("Invalid version number for best player")
		return
	with open(BEST_VERSION, 'w') as f:
		f.write(version)

def latest_version():
	versions = listdir(EXPORT_DIR)
	return sorted(versions, reverse=True)[0]

def logit_to_prob(logit):
	# logit is log(p/(1-p))
	# so logit to prob is (e^logit)/(1+(e^logit))
	return math.exp(logit)/(1+math.exp(logit))

def prob_to_logit(prob):
	# log(p/(1-p))
	return math.log(prob/(1-prob))
