.PHONY: all
all:parse

parse: parse.o
	g++ -o parse parse.o `mecab-config --cflags` `mecab-config --libs`

parse.o: parse.cpp
	g++ -c parse.cpp --std=c++14

.PHONY: clean
clean:
	rm -rf parse parse.o
