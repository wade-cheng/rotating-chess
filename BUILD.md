# Build

Instructions to get everything up and running. For my own sake as much as any readers'.

### pyinstaller
generate local executable: `pyinstaller main.spec`

### pygbag
build for wasm: `pygbag --build .` (omit `--build` to automatically host on localhost:8000)

run wasm: `python3 -m http.server 8000` from directory with `index.html`

### python source
`python3 main.py`