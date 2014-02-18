#!/bin/bash

./cool --lex bad.cl &&
python main.py bad.cl-lex &&
./cool --parse --out out bad.cl-lex &&
diff -b -B -E -w good.cl-ast out.cl-ast
