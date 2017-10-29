import chess
import hashlib
import math
import cairosvg
import time
import sys
import argparse
import moviepy.editor as mpy
from scipy.misc import imread
from chess import uci, pgn, svg

ROOT_DIR = "/Users/evanmdoyle/Programming/ChessAI/"
THREADS = 4

# Allow CLI toggle of GIF since it's slow
parser = argparse.ArgumentParser(description="Create custom Stockfish mirror matches.")
parser.add_argument("strength_levels", default=[20,20], nargs='*')
parser.add_argument("movetime", default=250, nargs='?')
parser.add_argument("--no_draw", action='store_true', help="Prevents engine from claiming draw.")
parser.add_argument("--gif", action='store_true', help="Save GIF of last played match.")
CLI_args = parser.parse_args()

GIF = CLI_args.gif

STRENGTH_1 = max(0, min(int(CLI_args.strength_levels[0]), 20))
STRENGTH_2 = max(0, min(int(CLI_args.strength_levels[1]), 20))

MOVETIME = CLI_args.movetime

CLAIM_DRAW = not CLI_args.no_draw

# Easily open a UCI connection to local stockfish
stockfish = uci.popen_engine(ROOT_DIR+"stockfish")
stockfish.uci()

stockfish.ucinewgame(lambda x: print("New Game Started"))

# Initialize game and board
game = chess.pgn.Game()
game.headers["White"] = stockfish.name
game.headers["Black"] = stockfish.name
board = chess.Board()
stockfish.position(board)
stockfish.setoption({'Threads': THREADS}, async_callback=
	(lambda x: print("Using "+str(THREADS)+" threads.")))

def update_strength(turn):
	if turn:
		stockfish.setoption({'Skill Level': STRENGTH_1})
	else:
		stockfish.setoption({'Skill Level': STRENGTH_2})

# To rasterize svg, convert to png and use pillow to read RGB
def write_tmp_png(svg, t):
    cairosvg.svg2png(bytestring=svg, write_to="/tmp/chesspng"+str(t)+".png")

# Use pillow to read RGB from temp pngs
def make_frame(t):
    return imread("/tmp/chesspng"+str(int(t))+".png")

# Main loop, gets moves from Stockfish, records them and updates the board
move_count = 1
write_tmp_png(chess.svg.board(board=board), move_count-1)
node = game
update_strength(board.turn)
(best_move,ponder_move) = stockfish.go(movetime=MOVETIME)
while(best_move is not None):
    if board.is_game_over(claim_draw=CLAIM_DRAW):
    	break
    best_move = chess.Move.from_uci(str(best_move))
    board.push(best_move)
    node = node.add_variation(best_move)
    stockfish.position(board)
    if GIF:
    	write_tmp_png(chess.svg.board(board=board), move_count)
    update_strength(board.turn)
    (best_move, ponder_move)=stockfish.go(movetime=MOVETIME)
    move_count += 1

# Use MoviePy to create a GIF from the png frames
if GIF:
	clip = mpy.VideoClip(make_frame=make_frame).set_duration(move_count)
	clip.write_gif("chess_game.gif",fps=1, fuzz=30, verbose=False)

	print("GIF written to 'chess_game.gif'")

print(board.result(claim_draw=CLAIM_DRAW))
print("In " + str(math.floor(move_count/2)) + " Moves")

game.headers["Result"] = board.result(claim_draw=CLAIM_DRAW)

final_fen = board.fen()

# Need to use the pgn module to export game to pgn
exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
game = game.accept(exporter)

# Pseudo-unique filename is 5 ASCII characters from the hash of the final FEN, save pgn
with open(ROOT_DIR+"StockfishMirrorMatches/"+hashlib.md5(final_fen.encode('utf-8')).hexdigest()[:5]+".pgn", 'w') as f:
	f.write(game)