import ply.yacc as yacc
import sys

tokens = (
	'PLUS', 'MINUS', 'TIMES', 'NUMBER'
	)

# tokens = (
# 	'at', 'case', 'class', 'colon', 'comma',
# 	 'divide', 'dot', 'else', 'equals', 'esac', 'false',
# 	 'fi', 'identifier', 'if', 'in', 'inherits',
# 	 'integer', 'isvoid', 'larrow', 'lbrace', 'le', 'let', 
# 	 'loop', 'lparen', 'lt', 'minus', 'new', 'not', 'of', 'plus',
# 	 'pool', 'rarrow', 'rbrace', 'rparen', 'semi', 'string', 'then', 
# 	 'tilde', 'times', 'true', 'type', 'while'
#     )

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
				s = raw_input('2 + 2')
			except EOFError:
				break
			if not s: continue
			result = parser.parse(s)
			print result
