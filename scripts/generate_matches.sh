#!/bin/bash
ROOT_DIR="/Users/evanmdoyle/Programming/ChessAI/"

echo "Playing combinations in range $1 to $2 at $3 repetitions each."
for i in $(seq 1 $3);
do
	for j in $(seq $1 $2);
	do
		for k in $(seq $1 $2);
		do
			echo "Playing $j vs. $k"
			python "$ROOT_DIR"wrapped_stockfish.py "$j" "$k"
		done
	done
done

echo "Processing all PGNs into heatmaps."
python "$ROOT_DIR"scripts/process_pgns.py