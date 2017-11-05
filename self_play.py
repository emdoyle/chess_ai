# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import chess
import os
import datetime
import numpy as np
import tensorflow as tf
import pychess_utils as util

from chess import pgn
from deepmind_mcts import MCTS

PGN_DIR = "/Users/evanmdoyle/Programming/ChessAI/ACZData/pgn/"
DATA_DIR = "/Users/evanmdoyle/Programming/ChessAI/ACZData/self_play.csv"
GAME_BATCH_SIZE = 1
ENGINE_NAME = "ACZ"
EXPORTER = chess.pgn.StringExporter(headers=True, variations=True, comments=True)

def decode_result(result, turn):
	if result == '1-0':
		return float(turn)
	if result == '0-1':
		return float(not turn)
	if result == '1/2-1/2':
		return 0.5
	return None

def extract_csv_string(arr):
	features = ','.join(map(str, arr))

def write_board_data(boards, mcts_policy_strings, result):
	with open(DATA_DIR, "a") as f:
		if len(boards) != len(mcts_policy_strings):
			print("Recorded different number of boards and policies.")
		for i in range(len(boards)):
			if board.turn:
				curr_result = decode_result(result, board.turn)
			board = util.expand_position(boards[i])
			policy = mcts_policy_strings[i]
			f.write(extract_csv_string(board+[policy]+[curr_result]))

def write_game_data(game):
	game = game.accept(EXPORTER)
	with open(PGN_DIR+util.latest_version()+"/"+str(
		len(os.listdir(PGN_DIR+util.latest_version()))), "w") as f:
		f.write(game)

def play_game():
	# Initialize a Monte Carlo Tree Search object with the default chess board
	# and default hyperparameters (see deepmind_mcts.py)
	game = chess.pgn.Game()
	board = chess.Board()
	mcts = MCTS(startpos=board)

	boards = []
	mcts_policy_strings = []

	while not board.is_game_over(claim_draw=True):
		# Build new tree
		mcts.build()
		boards.append(board)
		mcts_policy_strings.append(mcts.get_policy_string())
		move = mcts.best_move()
		# Execute the move selected by MCTS
		board.push(move)
		print(board)
		game.add_variation(move)
		# Salvage existing statistics about the position
		mcts = MCTS(startpos=board, prev_mcts=mcts)

	result = board.result(claim_draw=CLAIM_DRAW)
	write_board_data(boards, mcts_policy_strings, result)

	game.headers["White"] = ENGINE_NAME
	game.headers["Black"] = ENGINE_NAME
	game.headers["Date"] = datetime.date.today()
	game.headers["Event"] = "N/A"
	game.headers["Result"] = result
	write_game_data(game)
	return board

def main():
	for i in range(GAME_BATCH_SIZE):
		play_game()

if __name__ == "__main__":
    main()