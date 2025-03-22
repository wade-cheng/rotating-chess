all: test pygbag

test:
	pytest -v --doctest-modules compressjson.py test_all.py
	
pygbag:
	rm docs -r 
	pygbag --build --template pygbag.tmpl .
	cp -r build/web docs 
