import os
import numpy as np
import chess
import pychess_utils as util
from chess import pgn

PGN_DIR = os.fsencode('/Users/evanmdoyle/Programming/ChessAI/StockfishMirrorMatches/')
DATA_DIR = 'DerivedData/'
LOCAL_PATH = 'StockfishMirrorMatches/'
SQUARES = chess.SQUARES

for pgn_file in os.listdir(PGN_DIR):
	file_name = os.fsdecode(pgn_file)
	game = pgn.read_game(open(LOCAL_PATH+file_name, 'r'))
	board = game.board()
	moves = 0
	with open(DATA_DIR+"stockfishdata_"+file_name[:-4]+".csv", 'w') as f:
		for move in game.main_line():
			moves += 1
			heatmap = util.build_heatmap(board)
			for square in heatmap[:-1]:
				f.write(str(square)+",")
			f.write(str(heatmap[-1])+"\n")
			board.push(move)

	print("Should have just written data for " + str(moves) + " moves.")