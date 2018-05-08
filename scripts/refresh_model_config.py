import sys
sys.path.append(sys.path[0] + "/..")
import os

import pychess_utils as util

CONFIG_FILE = ".model_server_config"
VERSIONS = "versions: "
BASE_PATH = "base_path: "

def main():
	lines = []
	with open(CONFIG_FILE, 'r') as f:
		lines = f.readlines()
	with open(CONFIG_FILE, 'w') as f:
		for line in lines:
			if line.find(VERSIONS) != -1:
				line = line[:line.index(VERSIONS)+len(VERSIONS)]
				line += "[ " + str(util.latest_version()) + ", " + str(util.best_version()) + " ]\n"
			elif line.find(BASE_PATH) != -1:
				line = line[:line.index(BASE_PATH)+len(BASE_PATH)]
				line += "\""+os.getcwd()+"/Export/\""
			f.write(line)


if __name__ == "__main__":
	main()