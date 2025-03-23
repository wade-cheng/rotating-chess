all: test pygbag

test:
	uv run pytest -v --doctest-modules src/rotating_chess/compressjson.py tests
	
pygbag:
	rm docs -r 
	uv run pygbag --build --template pygbag.tmpl src/rotating_chess
	mv src/rotating_chess/build/web docs 
