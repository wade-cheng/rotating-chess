all: test pygbag

test:
	uv run pytest -v --doctest-modules compressjson.py test_all.py
	
pygbag:
	rm docs -r 
	pygbag --build --template pygbag.tmpl .
	cp -r build/web docs 
