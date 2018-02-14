for i in {1..500}
do
	python self_play.py
	python train.py
done