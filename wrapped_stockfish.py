import chess
import hashlib
import math
from chess import uci, pgn

ROOT_DIR = "/Users/evanmdoyle/Programming/ChessAI/"

# Easily open a UCI connection to local stockfish
stockfish = uci.popen_engine(ROOT_DIR+"stockfish")
stockfish.uci()

stockfish.ucinewgame(lambda x: print("New Game Started"))

game = chess.pgn.Game()
game.headers["White"] = stockfish.name
game.headers["Black"] = stockfish.name
board = chess.Board()
stockfish.position(board)

move_count = 1
node = game
(best_move,ponder_move) = stockfish.go()
while(best_move is not None):
	best_move = chess.Move.from_uci(str(best_move))
	board.push(best_move)
	node = node.add_variation(best_move)
	stockfish.position(board)
	(best_move, ponder_move)=stockfish.go()
	move_count += 1

print(board.result())
print("In " + str(math.floor(move_count/2)) + " Moves")

game.headers["Result"] = board.result()

final_fen = board.fen()

exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
game = game.accept(exporter)

with open(ROOT_DIR+"StockfishMirrorMatches/"+hashlib.md5(final_fen.encode('utf-8')).hexdigest()[:5]+".pgn", 'w') as f:
	f.write(game)