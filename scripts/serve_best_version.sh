#!/bin/bash
python scripts/refresh_model_config.py
wd=$(pwd)
model=$(head -n 1 "best_version.txt")
port=$(head -n 1 "port.txt")
tensorflow_model_server --port=$port --model_config_file=".model_server_config"