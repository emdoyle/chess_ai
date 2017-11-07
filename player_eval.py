# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import chess
import os
import datetime
import pychess_utils as util

from chess import pgn
from deepmind_mcts import MCTS

# This should eventually go up to 400
EVAL_GAMES = 20

board = chess.Board()
# latest version is default for MCTS
latest_player = MCTS(startpos=board)

# util grabs best version number from storage
best_player = MCTS(startpos=board, version=util.best_version())

def play_game(best_player_starts=True):
	board = chess.Board()

	turn = True
	if best_player_starts:
		player1 = best_player
		player2 = latest_player
	else:
		player1 = latest_player
		player2 = best_player

	while not board.is_game_over(claim_draw=True):
		if turn:
			player = player1
		else:
			player = player2

		# Build new tree
		player.build()
		move = player.best_move()
		# Execute the move selected by MCTS
		board.push(move)
		move_count += 1
		# Stop exploring so much after 20 moves
		if move_count == 20:
			next_temp = False
		print("Move " + str(move_count) + ": " + move.uci())
		print(board)
		# Salvage existing statistics about the position
		player = MCTS(startpos=board, prev_mcts=player, temperature=next_temp)
		turn = not turn

	latest_player_result = util.decode_result(board.result(claim_draw=True), not best_player_starts)

	return latest_player_result

for i in range(EVAL_GAMES):
	results = 0
	# Switch off who plays as white
	results += play_game(best_player_starts=(i % 2 == 0))

if results >= (EVAL_GAMES*0.55):
	# The new player won 55+% of the games and should be promoted to the best
	util.update_best_player(latest_player.version)