requirements:
	pip install -r requirements.txt

run:
	python tetris.py

style:
	ruff check . --fix

test:
	python test.py
