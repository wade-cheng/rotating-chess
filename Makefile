all: test pygbag

test:
	# can use eg: uv run pytest -v -k TestPromotion
	uv run pytest -v --doctest-modules src/rotating_chess/*.py tests
	
pygbag:
	echo "BROKEN :("
	exit 1
	rm docs -r 
	uv run pygbag --build --template pygbag.tmpl src
	mv src/build/web docs 

run:
	(cd src && uv run main.py)