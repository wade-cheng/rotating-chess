all: pyinstaller pygbag

# generate local executable
pyinstaller:
	# building with pyinstaller
	make dist

dist: *.py
	pyinstaller main.spec

# build for wasm
pygbag:
	# building with pygbag
	make build/web

# (omit `--build` to automatically host on localhost:8000)
build/web: *.py
	pygbag --build .
# update filesystem for github pages
	rm docs -r && cp -r build/web docs 

# python source
python:
	python3 main.py
