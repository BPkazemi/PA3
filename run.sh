#!/bin/bash

./cool --lex hello-world.cl &&
python main.py hello-world.cl-lex &&
./cool --parse --out out  hello-world.cl-lex &&
diff -b -B -E -w hello-world.cl-ast out.cl-ast
