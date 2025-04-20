all: test pygbag

test:
	# can use eg: uv run pytest -v -k TestPromotion
	uv run pytest -v --doctest-modules src/rotating_chess/*.py tests
	
pygbag:
	rm docs -rf
	rm src/build -rf
	uv run pygbag --build --template pygbag.tmpl --ume_block 0 --icon src/assets/favicon.png src/main.py
	mv src/build/web docs 

run:
	(cd src && uv run --env-file ../.env.dev main.py)

runfast:
	# running without debug on
	# (NOTE: consider adding a .env.prod? but we don't really use it.)
	(cd src && uv run main.py)

serve:
	(cd docs && python -m http.server)

clean:
	rm docs -rf
	rm src/build -rf
	rm __pycache__ -rf
	rm src/__pycache__ -rf
	rm src/rotating_chess/__pycache__ -rf
