import chess
import numpy as np

def num_squares_attacking(square, board):
	return len(board.attacks(square))

def build_heatmap(board):
	heatmap = [0 for k in range(64)]
	for square in chess.SQUARES:
		piece = board.piece_at(square)
		if piece is not None:
			color = piece.color
			num_attackers = len(board.attackers(not color, square))
			heatmap[square] = (num_attackers if color else -num_attackers)
	return heatmap

def print_heatmap(heatmap):
	for row in list(reversed(np.reshape(np.array(heatmap), (8,8)))):
		 print(row)