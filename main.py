import ply.yacc as yacc
import ply.lex as lex
import sys, os
import logging

from lexer import Lexer

precedence = (
	('nonassoc', 'larrow'),
	('nonassoc', 'not'),
	('nonassoc', 'equals', 'lt', 'le'),
    ('left', 'plus', 'minus'),
    ('left', 'times', 'divide'),
    ('nonassoc', 'isvoid'),
    ('right', 'tilde'),
    ('nonassoc', 'at'),
    ('nonassoc', 'dot')
)

########### Parser (token -> AST) #############

from compiler import ast

def lt_compare((left, right)):
	return ast.Compare(left, [('<', right),])
def le_compare((left, right)):
	return ast.Compare(left, [('<=', right),])
def eq_compare((left, right)):
	return ast.Compare(left, [('==', right),])

binary_ops = {
	"plus": ast.Add,
	"minus": ast.Sub,
	"times": ast.Mul,
	"divide": ast.Div,
	"lt": lt_compare,
	"le": le_compare,
	"equals": eq_compare
}

# program : [class semi]+
def p_program_one(p):
	'''PROGRAM : CLASSDEF semi'''
	p[0] = p[1]
def p_program_many(p):
	'''PROGRAM : PROGRAM CLASSDEF semi'''
	p[0] = p[1] + p[2]

def p_class_def(p):
	'''CLASSDEF : class type lbrace rbrace
				| class type lbrace FEATURE semi rbrace'''
	if len(p) == 5:
		p[0] = []
	else:
		p[0] = p[4]

def p_class_def_inherits(p):
	'''CLASSDEF : class type inherits type lbrace rbrace
				| class type inherits type lbrace FEATURE rbrace'''
	if len(p) == 7:
		p[0] = []
	else:
		p[0] = p[6]

def p_feature(p):
	'''FEATURE : identifier lparen FORMAL rparen colon type lbrace EXPR rbrace
				| identifier colon type
				| identifier colon type larrow EXPR'''
	if len(p) == 4:
		p[0] = []
	elif len(p) == 6:
		p[0] = p[5]
	else:
		p[0] = p[3] + p[8]

def p_formal(p):
	'''FORMAL : identifier colon type
			| FORMAL comma identifier colon type
			| '''
	if len(p) == 4:
		p[0] = []
	elif len(p) == 1:
		p[0] = []
	else:
		p[0] = p[1]

def p_expr_case(p):
	'''EXPR : case EXPR of identifier colon type rarrow EXPR semi esac'''
	p[0] = p[2] + p[8]

def p_expr_at_dot(p):
	'''EXPR : EXPR at type dot identifier lparen EXPR rparen
			| EXPR dot identifier lparen EXPR rparen
			'''
	if len(p) == 9:
		p[0] = p[1] + p[7]
	else:
		p[0] = p[1] + p[5]

def p_expr_let(p):
	'''EXPR : let identifier colon type in EXPR
			| let identifier colon type larrow EXPR in EXPR
			'''	
	if len(p) == 7:
		p[0] = p[6]
	else:
		p[0] = p[6] + p[8]

def p_expr_seconds(p):
	'''EXPR : lparen EXPR rparen
			| lbrace EXPR semi rbrace'''
	p[0] = p[2]


def p_expr_thirds(p):
	'''EXPR : identifier larrow EXPR
			| identifier lparen EXPR rparen'''
	p[0] = p[3]


def p_expr_firsts(p):
	'''EXPR : EXPR at type dot identifier lparen rparen
			| EXPR dot identifier lparen rparen'''
	p[0] = p[1]

def p_expr_conditionals(p):
	'''EXPR : if EXPR then EXPR else EXPR fi
			| while EXPR loop EXPR pool'''
	if p[1] == 'if':
		p[0] = p[2] + p[4] + p[6]
	else:
		p[0] = p[2] + p[4]


def p_expr_list(p):
	'''EXPR : EXPR comma EXPR
			| EXPR semi EXPR'''
	p[0] = p[1] + p[3]

def p_expr_doubles(p):
	'''EXPR : new type
			| isvoid EXPR
			| tilde EXPR
			| not EXPR
			| identifier lparen rparen'''
	p[0] = []



def p_expr_math(p):
	'''EXPR : EXPR plus EXPR
			| EXPR minus EXPR
			| EXPR times EXPR
			| EXPR divide EXPR
			| EXPR lt EXPR
			| EXPR le EXPR
			| EXPR equals EXPR'''
	# p[0] = binary_ops[p[2]]((p[1], p[3]))
	# p[0] = (p[1], p[2], p[3])
	p[0] = p[1] + p[3]


def p_expr_terminal(p):
	'''EXPR : identifier
			| integer
			| string
			| true
			| false'''
	# p[0] = ast.Const(p[1])
	p[0] = []
	


# def p_expression_plus(p):
#     'expression : expression plus expression'
#     print('expression : expression plus expression: {} + {}', p[1], p[3])
#     p[0] = p[1] + p[3]

# def p_expression_num(p):
# 	'expression : integer'
# 	print('expression : integer: {}', p[1])
# 	p[0] = p[1]

def p_empty(p):
	'empty :'
	print('empty :')
	pass

# Error rule for syntax errors
def p_error(p):
	if p is None:
		print "Error is None"
		exit()
	print "Error is {}".format(p)
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

		# Setup Logging
		logging.basicConfig(
		    level = logging.DEBUG,
		    filename = "parselog.txt",
		    filemode = "w",
		    format = "%(filename)10s:%(lineno)4d:%(message)s"
		)
		log = logging.getLogger()		

		# Build the parser
		parser = yacc.yacc(debug=True, debuglog = log)
		# print parser.productions

		while True:
			# try:
			# 	s = raw_input('ply > ')
			# except EOFError:
			# 	break
			# if not s: continue
			result = parser.parse(lexer = lexer)
			print result
