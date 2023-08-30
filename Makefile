requirements:
	pip install -r requirements.txt

run:
	python tetris.py

style:
	ruff check . --fix

test:
	python test.py

coverage:
	python -m coverage run -m unittest
	python -m coverage report -m --omit test.py --skip-covered
