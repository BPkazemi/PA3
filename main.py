import ply.yacc as yacc
import ply.lex as lex
import sys, os
import logging

from lexer import Lexer

precedence = (
	('nonassoc', 'larrow'),
	('nonassoc', 'not'),
	('left', 'equals', 'lt', 'le'),
    ('left', 'plus', 'minus'),
    ('left', 'times', 'divide'),
    ('left', 'let'),
    # ('left', 'semi'),
    ('nonassoc', 'isvoid'),
    ('right', 'tilde'),
    ('nonassoc', 'at'),
    ('nonassoc', 'dot')
)

########### AST  ##############
class Node:
	def __init__(self, type, children=None, leaf=None):
		self.type = type
		if children:
			self.children = children
		else:
			self.children = [ ]
		self.leaf = leaf

	def __repr__(self):
		return "Type: {}, num_children: {}, value: {}".format(self.type, len(self.children), self.leaf)

########### Parser (token -> AST) #############

# from compiler import ast

# def lt_compare((left, right)):
# 	return ast.Compare(left, [('<', right),])
# def le_compare((left, right)):
# 	return ast.Compare(left, [('<=', right),])
# def eq_compare((left, right)):
# 	return ast.Compare(left, [('==', right),])

# binary_ops = {
# 	"plus": ast.Add,
# 	"minus": ast.Sub,
# 	"times": ast.Mul,
# 	"divide": ast.Div,
# 	"lt": lt_compare,
# 	"le": le_compare,
# 	"equals": eq_compare
# }

def p_start(p):
	'''START : PROGRAM'''
	root = Node("Program", p[1], "PROGRAM")
	p[0] = root


def p_program_one(p):
	'''PROGRAM : PROGRAM CLASSDEF semi
			| CLASSDEF semi'''
	if len(p) == 4:
		# p[0] = p[1] + p[2]
		classes = p[1]
		classes.append(p[2])
		p[0] = classes
	else:	
		# p[0] = p[1]
		p[0] = [p[1]]

# def p_program_many(p):
# 	'''PROGRAM : PROGRAM CLASSDEF semi'''
# 	p[0] = p[1] + p[2]


def p_class_def(p):
	'''CLASSDEF : class type lbrace rbrace
				| class type lbrace FEATURE semi rbrace'''
	if len(p) == 5:
		# p[0] = []
		p[0] = Node("class_no_inherits", [], "class type lbrace rbrace")
	else:
		# p[0] = p[4]
		p[0] = Node("class_no_inherits", p[4], "class type lbrace FEATURE semi rbrace")

def p_class_def_inherits(p):
	'''CLASSDEF : class type inherits type lbrace rbrace
				| class type inherits type lbrace FEATURE semi rbrace'''
	if len(p) == 7:
		# p[0] = []
		p[0] = Node("class_inherits", [], "class type inherits type lbrace rbrace")
	else:
		# p[0] = p[6]
		p[0] = Node("class_inherits", p[6], "class type inherits type lbrace FEATURE semi rbrace")


def p_feature_helper(p):
	'''FEATURE :  FEATURE semi FEATURELIT
				| FEATURELIT'''
	if len(p) == 4:
		# p[0] = p[1] + p[3]
		if p[1] and p[3]:
			# print 'p1: {} and p3: {}'.format(p[1], p[3])
			features = p[1]
			features.append(p[3])
			p[0] = features
		elif p[1]:
			# print 'p1: {}'.format(p[1])
			p[0] = p[1]
		elif p[3]:
			# print 'p3: {}'.format(p[3])
			p[0] = [p[3]]
	else:
		# p[0] = p[1]
		p[0] = [p[1]]

# def p_feature_list(p):
# 	'''FEATURELIST : FEATURE semi FEATURELIST
# 					| '''
# 	if len(p) == 4:
# 		p[0] = p[1] + p[3]
# 	else:
# 		p[0] = []

def p_feature(p):
	'''FEATURELIT : identifier lparen FORMAL rparen colon type lbrace EXPR rbrace
				| identifier lparen rparen colon type lbrace EXPR rbrace
				| identifier colon type
				| identifier colon type larrow EXPR'''
	if len(p) == 4:
		# p[0] = []
		p[0] = Node("attribute_no_init", [], "identifier colon type")
	elif len(p) == 6:
		# p[0] = p[5]
		p[0] = Node("attribute_init", [p[5]], "identifier colon type larrow EXPR")
	elif len(p) == 9:
		# p[0] = p[7]
		p[0] = Node("method", [p[7]], "identifier lparen rparen colon type lbrace EXPR rbrace")
	else:
		# p[0] = p[3] + p[8]
		formals = p[3]
		expr = p[8]
		formals.append(expr)
		p[0] = Node("method", formals, "identifier lparen FORMAL rparen colon type lbrace EXPR rbrace")

def p_formal(p):
	'''FORMAL : FORMAL comma FORMALLIT
			| FORMALLIT'''
	if len(p) == 4:
		# p[0] = p[1] + p[3]
		formals = p[1]
		formals.append(p[3])
		p[0] = formals
	else:
		# p[0] = p[1]
		p[0] = [p[1]]

def p_formal_lit(p):
	'''FORMALLIT : identifier colon type'''
	# p[0] = []
	p[0] = Node("formal", [], "identifier colon type")

# def p_expr_case(p):
# 	'''EXPR : case EXPR of identifier colon type rarrow EXPR semi esac'''
# 	p[0] = p[2] + p[8]

def p_expr_case(p):
	'''EXPR : case EXPR of CASEHELPER esac'''
	# p[0] = p[2] + p[8]
	case_expr = Node("case_expression", [p[2]], "Case EXPR")
	children = [case_expr].extend(p[8])
	p[0] = Node("case", children, "case EXPR of CASEHELPER esac")

def p_case_helper(p):
	'''CASEHELPER : CASEHELPER CASELIT
					| CASELIT'''
	if len(p) == 3:
		# p[0] = p[1] + p[2]
		cases = p[1]
		cases.append(p[2])
		p[0] = cases
	else:
		# p[0] = p[1]
		p[0] = [p[1]]

def p_case_lit(p):
	'''CASELIT : identifier colon type rarrow EXPR semi'''
	# p[0] = p[5]
	p[0] = Node("case_element", [p[5]], "identifier colon type rarrow EXPR semi")

def p_expr_firsts(p):
	'''EXPR : EXPR at type dot identifier lparen rparen
			| EXPR dot identifier lparen rparen'''
	if p[2] == "at":
		p[0] = Node("dynamic_dispatch", [p[1]], "EXPR at type dot identifier lparen rparen")
	else:
		p[0] = Node("static_dispatch", [p[1]], "EXPR dot identifier lparen rparen")
	# p[0] = p[1]

def p_expr_at_dot(p):
	'''EXPR : EXPR at type dot identifier lparen EXPRLISTCOMMA rparen
			| EXPR dot identifier lparen EXPRLISTCOMMA rparen'''
	if len(p) == 9:
		# p[0] = p[1] + p[7]
		expression = Node("dynamic_exp", [p[1]], "EXPR")
		expression_list = Node("dynamic_params", p[7], "EXPR")
		children = [expression].extend(expression_list)
		p[0] = Node("dynamic_dispatch", children, "EXPR at type dot identifier lparen EXPRLISTCOMMA rparen")
	else:
		# p[0] = p[1] + p[5]
		expression = Node("static_exp", [p[1]], "EXPR")
		expression_list = Node("static_params", p[5], "EXPR")
		children = [expression].extend(expression_list)
		p[0] = Node("static_dispatch", children, "EXPR dot identifier lparen EXPRLISTCOMMA rparen")


def p_expr_let(p):
	'''EXPR : let identifier colon type LETHELPER in EXPR
			| let identifier colon type larrow EXPR LETHELPER in EXPR
			| let identifier colon type in EXPR
			| let identifier colon type larrow EXPR in EXPR
			'''	
	if len(p) == 8:
		expression_node = Node("expression", [p[7]], "EXPR")
		lets = p[5]
		lets.append(expression_node)
		p[0] = Node("let_statement_not_binding", lets , "let identifier colon type LETHELPER in EXPR")
		# p[0] = p[5] + p[7]
	elif len(p) == 10:
		expression_node = Node("expression", [p[9]], "EXPR")
		binding_node = Node("let_binding_expression", [p[6]], "EXPR")
		let_binding_node = Node("let_statement_binding", p[7], "let identifier colon type larrow EXPR LETHELPER in EXPR")
		# p[0] = p[6] + p[7] + p[9]
		p[0] = let_binding_node
	elif len(p) == 7:
		# p[0] = p[6]
		let_statement_node = Node("let_statement_not_binding", [p[6]], "let identifier colon type in EXPR")
		p[0] = let_statement_node
	else:
		# p[0] = p[6] + p[8]
		let_statement_node = Node("let_statement_binding", [p[6], p[8]], "let identifier colon type larrow EXPR in EXPR")
		p[0] = let_statement_node

def p_let_helper(p):
	'''LETHELPER : comma LETHELPERLIT LETHELPER
				| comma LETHELPERLIT'''
	if len(p) == 4:
		lets = p[2]
		lets.append(p[3])
		p[0] = lets
	else:
		p[0] = p[2]

def p_let_lit(p):
	'''LETHELPERLIT : identifier colon type
			| identifier colon type larrow EXPR'''
	if len(p) == 4:
		# p[0] = []
		p[0] = [Node("let_binding_no_init", [], "identifier colon type")]
	else:
		# p[0] = p[5]
		p[0] = [Node("let_binding_init", [p[5]], "identifier colon type larrow EXPR")]

def p_expr_seconds(p):
	'''EXPR : lparen EXPR rparen
			| lbrace EXPRLISTSEMI semi rbrace'''
	p[0] = p[2]
	if len(p) == 4:
		p[0] = Node("expression", [p[2]], "lparen EXPR rparen")
	else:
		p[0] = Node("expression", p[2], "lbrace EXPRLISTSEMI semi rbrace")

def p_expr_id_call(p):
	'''EXPR : identifier lparen rparen
			| identifier lparen EXPRLISTCOMMA rparen'''
	if len(p) == 4:
		p[0] = Node("expressions", [], "identifier lparen rparen")
	else:
		p[0] = Node("expressions", p[3], "identifier lparen EXPRLISTCOMMA rparen")

def p_expr_assign(p):
	'''EXPR : identifier larrow EXPR'''
	# p[0] = p[3]
	p[0] = Node("assignment", [p[3]], "identifier larrow EXPR")


def p_expr_conditionals(p):
	'''EXPR : if EXPR then EXPR else EXPR fi
			| while EXPR loop EXPR pool'''
	if p[1] == 'if':
		# p[0] = p[2] + p[4] + p[6]
		if_block = Node("if_block", [p[2]], "if")
		then_block = Node("then_block", [p[4]], "then")
		else_block = Node("else_block", [p[6]], "else")
		p[0] = Node("if_statement", [if_block, then_block, else_block], "if EXPR then EXPR else EXPR fi")
	else:
		while_node = Node("while_block", [p[2]], "while")
		loop_node = Node("loop_block", [p[4]], "loop")
		while_loop_node = Node("while_loop", [while_node, loop_node], "while EXPR loop EXPR pool")
		p[0] = while_loop_node
		# p[0] = p[2] + p[4]


# def p_expr_list(p):
# 	'''EXPR : EXPR semi EXPR
# 			| EXPR comma EXPR'''
# 	p[0] = p[1] + p[3]

def p_expr_list_comma(p):
	'''EXPRLISTCOMMA : EXPRLISTCOMMA comma EXPR
			| EXPR'''
	if len(p) == 4:
		exprs = p[1]
		exprs.append(Node("expression", [p[3]], "EXPRLISTCOMMA comma EXPR"))
		p[0] = exprs
	else:
		p[0] = [Node("expression", [p[1]], "EXPR")]

def p_expr_list_semi(p):
	'''EXPRLISTSEMI : EXPRLISTSEMI semi EXPR
			| EXPR'''
	if len(p) == 4:
		if p[1]:
			exprs = p[1]
			exprs.append( Node("express", [p[3]], "EXPRLISTSEMI semi EXPR"))
			p[0] = exprs
	else:
		p[0] = [Node("expression", [p[1]], "EXPR")]


def p_expr_doubles(p):
	'''EXPR : isvoid EXPR
			| tilde EXPR
			| not EXPR'''
	p[0] = Node("unary", [p[2]], p[1])

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
	p[0] = Node("binop", [p[1], p[3]], p[2])


def p_expr_terminal(p):
	'''EXPR : identifier
			| integer
			| string
			| true
			| false
			| new type'''
	# p[0] = ast.Const(p[1])
	p[0] = Node("terminal", [], p[1])
	

def recurce_tree(tree):
	print "Body: {}".format(tree)
	for elem in tree.children:
		print " --- ", elem
	if not len(tree.children):
		return
	for child in tree.children:
		recurce_tree(child)

# def p_expression_plus(p):
#     'expression : expression plus expression'
#     print('expression : expression plus expression: {} + {}', p[1], p[3])
#     p[0] = p[1] + p[3]

# def p_expression_num(p):
# 	'expression : integer'
# 	print('expression : integer: {}', p[1])
# 	p[0] = p[1]

# def p_empty(p):
# 	'empty :'
# 	print('empty :')
# 	pass

# Error rule for syntax errors
def p_error(p):
	if p is None:
		print "Error is None"
		# print "Root: {}".format(ast.type)
		# exit()
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
		parser = yacc.yacc(debug=True)
		# print parser.productions

		while True:
			# try:
			# 	s = raw_input('ply > ')
			# except EOFError:
			# 	break
			# if not s: continue
			result = parser.parse(lexer = lexer)
			recurce_tree(result)
			break
			# print result
