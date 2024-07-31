pygbag:
	rm docs -r 
	pygbag --build --template pygbag.tmpl .
	cp -r build/web docs 
