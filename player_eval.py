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

# latest version is default for MCTS
latest_player = MCTS(startpos=chess.Board())

# util grabs best version number from storage
best_player = MCTS(startpos=chess.Board(), version=util.best_version())

def play_game(best_player_starts=True):
	turn = True
	if best_player_starts:
		player1 = best_player
		player2 = latest_player
	else:
		player1 = latest_player
		player2 = best_player

	board = player1.startpos
	move_count = 0
	next_temp = True
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
		if turn:
			player2 = MCTS(startpos=board, prev_mcts=player, temperature=next_temp, startcolor=board.turn)
		else:
			player1 = MCTS(startpos=board, prev_mcts=player, temperature=next_temp, startcolor=board.turn)
		turn = not turn

	latest_player_result = util.decode_result(board.result(claim_draw=True), not best_player_starts)

	return latest_player_result

def main():
	for i in range(EVAL_GAMES):
		results = 0
		# Switch off who plays as white
		results += play_game(best_player_starts=(i % 2 == 0))

	if results >= (EVAL_GAMES*0.55):
		print("New player won!")
		# The new player won 55+% of the games and should be promoted to the best
		util.update_best_player(latest_player.version)
	else:
		print("Old player won!")

if __name__ == "__main__":
    main()