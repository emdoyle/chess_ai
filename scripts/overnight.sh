for i in {1..500}
do
	python scripts/refresh_model_config.py
	python self_play.py
	python train.py
	python player_eval.py
done