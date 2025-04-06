all: test pygbag

test:
	# can use eg: uv run pytest -v -k TestPromotion
	uv run pytest -v --doctest-modules src/rotating_chess/*.py tests
	
pygbag:
	rm docs -rf
	rm src/build -rf
	uv run pygbag --build --template pygbag.tmpl src/main.py
	mv src/build/web docs 

run:
	(cd src && uv run main.py)