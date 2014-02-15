import ply.yacc as yacc
import sys

from lexer import tokens

# tokens = (
# 	"integer", "class", "type", "case",
# 	"at", "equals", "larrow", "rarrow",
# 	"lbrace", "rbrace", "le", "lt", "semi",
# 	"colon", "tilde", "lparen", "rparen",
# 	"divide", "times", "plus", "minus", 
# 	"else", "comma", "dot", "false", "true",
# 	"fi", "if", "inherits", "in", "isvoid",
# 	"let", "loop", "new", "not", "of",
# 	"pool", "then", "while", "esac", "string",
# 	"identifier"
# 	)

def p_expression_plus(p):
    'expression : expression PLUS expression'
    p[0] = p[1] + p[3]

def p_expression_num(p):
	'expression : NUMBER'
	p[0] = p[1]

# Error rule for syntax errors
def p_error(p):
    print "Syntax error in input!"

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Please provide a .cl-lex file as the only argument."
	else:
		lex_fname = sys.argv[1]

		with open(lex_fname) as f:
			contents = f.readlines()

		# Build the parser
		parser = yacc.yacc()

		while True:
			try:
				s = raw_input('ply > ')
			except EOFError:
				break
			if not s: continue
			result = parser.parse(s)
			print type(result)
