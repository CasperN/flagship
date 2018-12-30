info:
	@ cat makefile

help:
	python3 flagship.py --help

test:
	black .
	./test.py
