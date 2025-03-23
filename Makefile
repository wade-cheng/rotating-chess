all: test pygbag

test:
	uv run pytest -v --doctest-modules src/rotating_chess/compressjson.py tests
	
pygbag:
	rm docs -r 
	uvx pygbag@latest --build --template pygbag.tmpl src/rotating_chess
	cp -r build/web docs 
