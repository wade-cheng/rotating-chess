all: test pygbag

test:
	uv run pytest -v --doctest-modules src/rotating_chess/compressjson.py tests
	
pygbag:
	rm docs -r 
	uvx pygbag@0.8.6 --build --template pygbag.tmpl .
	cp -r build/web docs 
