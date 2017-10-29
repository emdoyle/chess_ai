#!/bin/bash

TARGET_DIR="/Users/evanmdoyle/Programming/ChessAI/DerivedData/heatmaps/"

for filename in "$TARGET_DIR"*; do
	base=${filename##*/}
	stripped=${base#stockfishdata}
	new="heatmap$stripped"
	mv $filename "$TARGET_DIR"$new
done