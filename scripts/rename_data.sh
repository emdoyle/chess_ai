#!/bin/bash

TARGET_DIR="/Users/evanmdoyle/Programming/ChessAI/DerivedData/"
SRC_DIR="$TARGET_DIR$1s/"
DST_DIR="$TARGET_DIR$2s/"

mkdir DST_DIR

for filename in "$SRC_DIR"*; do
	base=${filename##*/}
	stripped=${base#$1}
	new="$2$stripped"
	mv $filename "$DST_DIR"$new
done