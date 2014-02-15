import ply.yacc as yacc
import ply.lex as lex
import sys, os

from lexer import Lexer

def p_expression_plus(p):
    'expression : expression plus expression'
    print('expression : expression plus expression')
    p[0] = p[1] + p[3]

def p_expression_num(p):
	'expression : integer'
	print('expression : integer')
	p[0] = p[1]

# Error rule for syntax errors
def p_error(p):
    print "Syntax error in input!"
    exit()

def read_tokens_create_lexer(filename):
	if os.path.exists(filename):
		three_liners = ("type", "identifier", "string", "integer")

		# Open the cl-lex file and read all lines
		with open(lex_fname) as f:
			contents = f.readlines()

		index = 0
		lexer = Lexer()
		while index < len(contents):
			# Read in the lexing tokens and add to Lexer
			line_no = contents[index].rstrip()
			token_type = contents[index+1].rstrip()
			value = None
			# print "{} in three_liners: {}".format(token_type, token_type in three_liners)
			if token_type in three_liners:
				value = contents[index+2].rstrip()
				index += 3
			else:
				index += 2
			# print("Adding Type: {}, LineNo: {}, Value:{}\n".format(token_type, line_no, value))
			lexer.add_token(token_type, line_no, value)
		return lexer


	else:
		print "File Does Not Exist."
		return None

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Please provide a .cl-lex file as the only argument."
	else:
		lex_fname = sys.argv[1]

		lexer = read_tokens_create_lexer(lex_fname)
		tokens = lexer.token_types

		# Build the parser
		parser = yacc.yacc()

		while True:
			# try:
			# 	s = raw_input('ply > ')
			# except EOFError:
			# 	break
			# if not s: continue
			result = parser.parse(lexer = lexer)
			print result
