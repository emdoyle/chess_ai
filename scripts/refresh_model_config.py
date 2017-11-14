import sys
sys.path.append(sys.path[0] + "/..")

import pychess_utils as util

CONFIG_FILE = "/Users/evanmdoyle/Programming/ChessAI/serving/tensorflow_serving/config/model_config.txt"
INDICATOR = "versions: "

def main():
	lines = []
	with open(CONFIG_FILE, 'r') as f:
		lines = f.readlines()
	with open(CONFIG_FILE, 'w') as f:
		for line in lines:
			if line.find(INDICATOR) != -1:
				line = line[:line.index(INDICATOR)+len(INDICATOR)]
				line += "[ " + str(util.latest_version()) + ", " + str(util.best_version()) + " ]\n"
			f.write(line)


if __name__ == "__main__":
	main()