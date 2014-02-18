#!/bin/bash

./cool --lex good.cl &&
python main.py good.cl-lex &&
./cool --parse --out out good.cl-lex &&
diff -b -B -E -w good.cl-ast out.cl-ast
