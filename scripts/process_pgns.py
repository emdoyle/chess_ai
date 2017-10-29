# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import os
import numpy as np
import chess
import pychess_utils as util
from chess import pgn

PKG_DIR = '/Users/evanmdoyle/Programming/ChessAI/'
PGN_DIR = os.fsencode(PKG_DIR+'StockfishMirrorMatches/')
OFF_HEATMAP_DIR = PKG_DIR+'DerivedData/off_heatmaps/'
DEF_HEATMAP_DIR = PKG_DIR+'DerivedData/def_heatmaps/'
LABEL_DIR = PKG_DIR+'DerivedData/labels/'
MATCHES_PATH = PKG_DIR+'StockfishMirrorMatches/'
SQUARES = chess.SQUARES

for pgn_file in os.listdir(PGN_DIR):
	file_name = os.fsdecode(pgn_file)
	game = pgn.read_game(open(MATCHES_PATH+file_name, 'r'))

	board = game.board()
	moves = 0
	with open(LABEL_DIR+"labels_"+file_name[:-4]+".csv", 'w') as f:
		for move in game.main_line():
			moves += 1
			label = move.uci()
			f.write(label+'\n')
			board.push(move)

	print("Wrote Labels for " + str(moves) + " moves.")

	board = game.board()
	moves = 0
	with open(DEF_HEATMAP_DIR+"def_heatmaps_"+file_name[:-4]+".csv", 'w') as f:
		for move in game.main_line():
			moves += 1
			heatmap = util.build_def_heatmap(board)
			for square in heatmap[:-1]:
				f.write(str(square)+",")
			f.write(str(heatmap[-1])+"\n")
			board.push(move)

	print("Wrote Defensive Heatmap for " + str(moves) + " moves.")

	board = game.board()
	moves = 0
	with open(OFF_HEATMAP_DIR+"off_heatmaps_"+file_name[:-4]+".csv", 'w') as f:
		for move in game.main_line():
			moves += 1
			heatmap = util.build_off_heatmap(board)
			for square in heatmap[:-1]:
				f.write(str(square)+",")
			f.write(str(heatmap[-1])+"\n")
			board.push(move)

	print("Wrote Offensive Heatmap for " + str(moves) + " moves.")