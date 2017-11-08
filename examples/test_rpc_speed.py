# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import time
import chess
import pychess_utils as util
from rpc_client import PredictClient

def test(client, size):
	begin = time.time()
	for i in range(size):
		client.predict(util.expand_position(chess.Board()), signature_name='policy')
	serial_time = time.time()-begin
	print(str(size) + " predictions done separately took: " + str(serial_time))

	begin = time.time()
	client.predict([util.expand_position(chess.Board()) for i in range(size)], request_timeout=size, signature_name='policy', shape=[size, 832])
	batch_time = time.time()-begin
	print(str(size) + " predictions done in one batch took: " + str(batch_time))

	print("Per prediction times: " + str(serial_time/size) + " vs. " + str(batch_time/size))
	print("Savings per prediction: " + str((serial_time/size)-(batch_time/size)))


def main():
	client = PredictClient('127.0.0.1', 9000, 'default', int(util.latest_version()))
	print("Doing one dummy prediction...")
	client.predict(util.expand_position(chess.Board()))
	print("Beginning test")

	for size in [pow(2, x) for x in range(8)]:
		test(client, size)

if __name__ == "__main__":
	main()