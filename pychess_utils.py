import chess
import numpy as np

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

