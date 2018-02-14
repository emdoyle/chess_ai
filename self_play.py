# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import chess
import os
import time
import datetime
import numpy as np
import pychess_utils as util

from chess import pgn
from deepmind_mcts import MCTS

PGN_DIR = "/Users/evanmdoyle/Programming/ChessAI/ACZData/pgn/"
DATA_DIR = "/Users/evanmdoyle/Programming/ChessAI/ACZData/self_play.csv"
GAME_BATCH_SIZE = 1
CLAIM_DRAW = True
ENGINE_NAME = "ACZ"

def extract_csv_string(arr):
	return ','.join(map(str, arr))

def write_board_data(boards, mcts_policy_strings, result):
	with open(DATA_DIR, "a") as f:
		if len(boards) != len(mcts_policy_strings):
			print("Recorded different number of boards and policies.")
		for i in range(len(boards)):
			board = boards[i]
			curr_result = util.decode_result(result, board.turn)
			board = util.expand_position(boards[i])
			policy = mcts_policy_strings[i]
			f.write(extract_csv_string(board+[policy]+[curr_result])+"\n")

def write_game_data(game):
	game = game.accept(chess.pgn.StringExporter(headers=True, variations=True, comments=True))
	if not os.path.exists(PGN_DIR+str(util.best_version())):
		os.makedirs(PGN_DIR+str(util.best_version()))
	with open(PGN_DIR+str(util.best_version())+"/"+str(
		len(os.listdir(PGN_DIR+str(util.best_version()))))+".pgn", "w") as f:
		f.write(game)

def play_game():
	# Initialize a Monte Carlo Tree Search object with the default chess board
	# and default hyperparameters (see deepmind_mcts.py)
	game = chess.pgn.Game()
	board = chess.Board()
	mcts = MCTS(version=util.best_version(), startpos=board)

	boards = []
	mcts_policy_strings = []
	move_count = 0
	next_temp = True

	# I believe his works because the game is implemented as a tree of moves and it
	# isn't fully hidden.  I assume add_variation() creates an edge to a new node and
	# returns it  while updating a value on the source node. 
	# Thus, 'game' still refers to the root GameNode while 'node' refers to the deepest
	# or final node in the tree. TODO: Check source code
	node = game

	while not board.is_game_over(claim_draw=True):
		begin = time.time()
		# Build new tree
		mcts.build()
		boards.append(board)
		mcts_policy_strings.append(mcts.get_policy_string())
		move = mcts.best_move()
		# Execute the move selected by MCTS
		board.push(move)
		move_count += 1
		# Stop exploring so much after 15 moves
		if move_count == 15:
			next_temp = False
		print("Move " + str(move_count) + ": " + move.uci())
		print(board)
		node = node.add_variation(move)
		# Salvage existing statistics about the position
		mcts = MCTS(startpos=board, prev_mcts=mcts, temperature=next_temp)
		time_elapsed = time.time() - begin
		print("Time elapsed from start of build to init next MCTS: " + str(time_elapsed))

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