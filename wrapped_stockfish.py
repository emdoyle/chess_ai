import chess
import hashlib
import math
import cairosvg
import time
import copy
import moviepy.editor as mpy
from scipy.misc import imread
from chess import uci, pgn, svg

ROOT_DIR = "/Users/evanmdoyle/Programming/ChessAI/"

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
BOARDS = [board]

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
(best_move,ponder_move) = stockfish.go(movetime=500)
while(best_move is not None):
    if board.can_claim_draw():
        break
    best_move = chess.Move.from_uci(str(best_move))
    board.push(best_move)
    node = node.add_variation(best_move)
    stockfish.position(board)
    BOARDS.append(copy.deepcopy(board))
    write_tmp_png(chess.svg.board(board=board), move_count)
    (best_move, ponder_move)=stockfish.go(movetime=500)
    move_count += 1

# Use MoviePy to create a GIF from the png frames
clip = mpy.VideoClip(make_frame=make_frame).set_duration(move_count)
clip.write_gif("chess_game.gif",fps=1, fuzz=30, verbose=False)

print("GIF written to 'chess_game.gif'")

print(board.result())
print("In " + str(math.floor(move_count/2)) + " Moves")

game.headers["Result"] = board.result()

final_fen = board.fen()

# Need to use the pgn module to export game to pgn
exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
game = game.accept(exporter)

# Pseudo-unique filename is 5 ASCII characters from the hash of the final FEN, save pgn
with open(ROOT_DIR+"StockfishMirrorMatches/"+hashlib.md5(final_fen.encode('utf-8')).hexdigest()[:5]+".pgn", 'w') as f:
	f.write(game)