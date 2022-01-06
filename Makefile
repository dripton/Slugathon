all: black mypy test build install

build:
	python3 setup.py build

install: build
	sudo python3 setup.py install

mypy:
	mypy --disallow-untyped-calls --disallow-untyped-defs slugathon

black:
	black slugathon/

test:
	pytest

clean:
	rm -rf build/ .pytest_cache/ .mypy_cache/
