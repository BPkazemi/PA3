import yacc
import sys, os
# import lexer

precedence = (
	('nonassoc', 'larrow'),
	('nonassoc', 'not'),
	('left', 'equals', 'lt', 'le'),
    ('left', 'plus', 'minus'),
    ('left', 'times', 'divide'),
    ('left', 'let'),
    ('nonassoc', 'isvoid'),
    ('right', 'tilde'),
    ('nonassoc', 'at'),
    ('nonassoc', 'dot')
)

########### Lexer #############
class Token:
	'''
	The Token Class. Holds a type, line number, and value if necessary
	'''

	def __init__(self, token_type, line_no, value=None):
		self.type = token_type
		self.line_no = line_no
		self.value = (token_type, value, line_no)

	def __repr__(self):
		return "Token{0}".format(self.value)


class Lexer:
	# List of Token names
	token_types = (
	"integer", "class", "type", "case",
	"at", "equals", "larrow", "rarrow",
	"lbrace", "rbrace", "le", "lt", "semi",
	"colon", "tilde", "lparen", "rparen",
	"divide", "times", "plus", "minus", 
	"else", "comma", "dot", "false", "true",
	"fi", "if", "inherits", "in", "isvoid",
	"let", "loop", "new", "not", "of",
	"pool", "then", "while", "esac", "string",
	"identifier"
	)

	def __init__(self):
		self.tokens = []

	def add_token(self, token_type, line_no, value=None):
		if token_type in self.token_types:
			t = Token(token_type, line_no, value)
		else:
			print 'Invalid Token Type'
			return
		self.tokens.append(t)

	def token(self):
		if not self.tokens:
			return None
		else:
			elem = self.tokens[0]
			del(self.tokens[0])
			return elem


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
		return "Type: {0}, num_children: {1}, value: {2}".format(self.type, len(self.children), self.leaf)

########### Parser (token -> AST) #############

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

def p_class_def(p):
	'''CLASSDEF : class type lbrace rbrace
				| class type lbrace FEATURE semi rbrace'''
	if len(p) == 5:
		# p[0] = []
		p[0] = Node("class_no_inherits", [], p[2])
	else:
		# p[0] = p[4]
		p[0] = Node("class_no_inherits", p[4], p[2])

def p_class_def_inherits(p):
	'''CLASSDEF : class type inherits type lbrace rbrace
				| class type inherits type lbrace FEATURE semi rbrace'''
	if len(p) == 7:
		# p[0] = []
		value = p[2]
		value = (value[0],value[1],value[2], p[4])
		p[0] = Node("class_inherits", [], value)
	else:
		# p[0] = p[6]
		value = p[2]
		value = (value[0],value[1],value[2], p[4])
		p[0] = Node("class_inherits", p[6], value)


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

def p_feature(p):
	'''FEATURELIT : identifier lparen FORMAL rparen colon type lbrace EXPR rbrace
				| identifier lparen rparen colon type lbrace EXPR rbrace
				| identifier colon type
				| identifier colon type larrow EXPR'''
	if len(p) == 4:
		# p[0] = []
		p[0] = Node("attribute_no_init", [], (p[1], p[3]))
	elif len(p) == 6:
		# p[0] = p[5]
		p[0] = Node("attribute_init", [p[5]], (p[1], p[3]))
	elif len(p) == 9:
		# p[0] = p[7]
		p[0] = Node("method", [], {"formals": [], "expression": p[7], "identifier": p[1], "type": p[5]})
	else:
		# p[0] = p[3] + p[8]
		formals = p[3]
		expr = p[8]
		p[0] = Node("method", formals, {"formals": formals, "expression": expr, "identifier": p[1], "type": p[6]})

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
	p[0] = Node("formal", [], (p[1], p[3]))

def p_expr_case(p):
	'''EXPR : case EXPR of CASEHELPER esac'''
	# p[0] = p[2] + p[8]
	# case_expr = Node("case_expression", [p[2]], "Case EXPR")
	# children = [case_expr].extend(p[8])
	p[0] = Node("case", p[4], (p[1], p[2]))

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
	p[0] = Node("case_element", [p[5]], (p[1], p[3]))

def p_expr_firsts(p):
	'''EXPR : EXPR at type dot identifier lparen rparen
			| EXPR dot identifier lparen rparen'''
	if len(p) == 8:
		p[0] = Node("static_dispatch", [], {"expression": p[1], "method": p[5], "type": p[3], "lineno": p[2][2]})
	else:
		p[0] = Node("dynamic_dispatch", [], {"expression": p[1], "method": p[3], "lineno": p[2][2]})
	# p[0] = p[1]

def p_expr_at_dot(p):
	'''EXPR : EXPR at type dot identifier lparen EXPRLISTCOMMA rparen
			| EXPR dot identifier lparen EXPRLISTCOMMA rparen'''
	if len(p) == 9:
		# p[0] = p[1] + p[7]
		expression = p[1]#Node("static_exp", [p[1]], "EXPR")
		expression_list = p[7]#Node("static_params", p[7], "EXPR")
		# children = [expression].extend(expression_list)
		p[0] = Node("static_dispatch", expression_list, {"expression": expression, "method": p[5], "type": p[3], "lineno": p[2][2]})
	else:
		# p[0] = p[1] + p[5]
		expression = p[1]#Node("dynamic_exp", [p[1]], "EXPR")
		expression_list = p[5]#Node("dynamic_params", p[5], "EXPR")
		# children = [expression].extend(expression_list)
		p[0] = Node("dynamic_dispatch", expression_list, {"expression": expression, "method": p[3], "lineno": p[2][2]})


def p_expr_let(p):
	'''EXPR : let identifier colon type LETHELPER in EXPR
			| let identifier colon type larrow EXPR LETHELPER in EXPR
			| let identifier colon type in EXPR
			| let identifier colon type larrow EXPR in EXPR
			'''	
	if len(p) == 8:
		binding_node = [Node("let_binding_no_init", [], {"identifier": p[2], "type": p[4]})]
		binding_node.extend(p[5])
		bindings = binding_node
		# print "Bindings1: {}".format(bindings)
		p[0] = Node("let_statement", [p[7]] , {"let":p[1], "bindings": bindings } )
		# p[0] = p[5] + p[7]
	elif len(p) == 10:
		binding_node = [Node("let_binding_init", [p[6]], {"identifier": p[2], "type": p[4]})]
		binding_node.extend(p[7])
		bindings = binding_node
		# print "Bindings2: {}".format(bindings)
		let_binding_node = Node("let_statement", [p[9]], {"let": p[1], "bindings": bindings})
		# p[0] = p[6] + p[7] + p[9]
		p[0] = let_binding_node
	elif len(p) == 7:
		# p[0] = p[6]
		binding_node = Node("let_binding_no_init", [], {"identifier": p[2], "type": p[4]})
		# print "Bindings3: {}".format([binding_node])
		let_statement_node = Node("let_statement", [p[6]], {"let": p[1], "bindings": [binding_node]})
		p[0] = let_statement_node
	else:
		# p[0] = p[6] + p[8]
		binding_node = Node("let_binding_init", [p[6]], {"identifier": p[2], "type": p[4]})
		# print "Bindings4: {}".format([binding_node])
		let_statement_node = Node("let_statement", [p[8]], {"let": p[1], "bindings": [binding_node]})
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
		p[0] = [Node("let_binding_no_init", [], {"identifier": p[1], "type": p[3]})]
	else:
		# p[0] = p[5]
		p[0] = [Node("let_binding_init", [p[5]], {"identifier": p[1], "type": p[3]})]

def p_expr_seconds(p):
	'''EXPR : lparen EXPR rparen
			| lbrace EXPRLISTSEMI semi rbrace'''
	p[0] = p[2]
	if len(p) == 4:
		p[0] = Node("parens", [p[2]], "lparen EXPR rparen")
	else:
		p[0] = Node("block", p[2], p[1])

def p_expr_id_call(p):
	'''EXPR : identifier lparen rparen
			| identifier lparen EXPRLISTCOMMA rparen'''
	if len(p) == 4:
		p[0] = Node("self_dispatch", [], p[1])
	else:
		p[0] = Node("self_dispatch", p[3], p[1])

def p_expr_assign(p):
	'''EXPR : identifier larrow EXPR'''
	# p[0] = p[3]
	p[0] = Node("assign", [p[3]], p[1])


def p_expr_conditionals(p):
	'''EXPR : if EXPR then EXPR else EXPR fi
			| while EXPR loop EXPR pool'''
	if len(p) == 8:
		# p[0] = p[2] + p[4] + p[6]
		# if_block = Node("if_block", [p[2]], "if")
		# then_block = Node("then_block", [p[4]], "then")
		# else_block = Node("else_block", [p[6]], "else")
		p[0] = Node("if", [p[2], p[4], p[6]], p[1])
	else:
		# while_node = Node("while_block", [p[2]], "while")
		# loop_node = Node("loop_block", [p[4]], "loop")
		while_loop_node = Node("while", [p[2], p[4]], p[1])
		p[0] = while_loop_node
		# p[0] = p[2] + p[4]


def p_expr_list_comma(p):
	'''EXPRLISTCOMMA : EXPRLISTCOMMA comma EXPR
			| EXPR'''
	if len(p) == 4:
		exprs = p[1]
		exprs.append( p[3] ) #Node("expression", [p[3]], "EXPRLISTCOMMA comma EXPR"))
		p[0] = exprs
	else:
		p[0] = [ p[1] ] #Node("expression", [p[1]], "EXPR")]

def p_expr_list_semi(p):
	'''EXPRLISTSEMI : EXPRLISTSEMI semi EXPR
			| EXPR'''
	if len(p) == 4:
		if p[1]:
			exprs = p[1]
			exprs.append( p[3] )#Node("express", [p[3]], "EXPRLISTSEMI semi EXPR"))
			p[0] = exprs
	else:
		p[0] = [ p[1] ]# Node("expression", [p[1]], "EXPR")]


def p_expr_doubles(p):
	'''EXPR : isvoid EXPR
			| tilde EXPR
			| not EXPR'''
	p[0] = Node(p[1][0], [p[2]], p[1])

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
	p[0] = Node(p[2][0], [p[1], p[3]], p[2])

def p_expr_terminal(p):
	'''EXPR : identifier
			| integer
			| string
			| true
			| false
			| new type'''
	# p[0] = ast.Const(p[1])
	if p[1][0] == "new":
		p[0] = Node(p[1][0], [], (p[1], p[2]))
	else:
		p[0] = Node(p[1][0], [], p[1])
	

def print_tree(tree, depth):
	print "--"*depth, "Body: {0}".format(tree)
	if not len(tree.children):
		return
	for child in tree.children:
		print_tree(child, depth+1)

output = ""

def output_as_identifier(value):
	return "{0}\n{1}\n".format(value[2], value[1])

def recurse_tree(tree):
	global output
	if tree.type == "Program":
		# Output list of classes
		output += "{0}\n".format(len(tree.children))
		# f.write()
	elif tree.type == "class_inherits":
		output += output_as_identifier(tree.leaf)
		output += "inherits \n"
		output += output_as_identifier(tree.leaf[3])
		output += "{0}\n".format(len(tree.children))
		# f.write(output)
	elif tree.type == "class_no_inherits":
		output += output_as_identifier(tree.leaf)
		output += "no_inherits \n"
		output += "{0}\n".format(len(tree.children))
		# f.write(output)
	elif tree.type == "method":
		output += "method\n"
		output += output_as_identifier(tree.leaf["identifier"])
		# f.write(output)
		output += "{0}\n".format(len(tree.leaf["formals"]))
		for formal in tree.leaf["formals"]:
			recurse_tree(formal)
		output += output_as_identifier(tree.leaf["type"])
		recurse_tree(tree.leaf["expression"])
		return
	elif tree.type == "attribute_no_init":
		output += "attribute_no_init \n"
		output += output_as_identifier(tree.leaf[0])
		output += output_as_identifier(tree.leaf[1])
		# f.write(output)
	elif tree.type == "attribute_init":
		output += "attribute_init \n"
		output += output_as_identifier(tree.leaf[0])
		output += output_as_identifier(tree.leaf[1])
		# f.write(output)
	elif tree.type == "formal":
		output += output_as_identifier(tree.leaf[0])
		output += output_as_identifier(tree.leaf[1])
		# f.write(output)
	elif tree.type == "integer" or tree.type == "string" :
		output += "{0}\n{1}\n{2}\n".format(tree.leaf[2], tree.leaf[0], tree.leaf[1])
		# f.write(output)
	elif tree.type == "true" or tree.type == "false":
		output += "{0}\n{1}\n".format(tree.leaf[2], tree.leaf[0])
		# f.write(output)
	elif tree.type == "identifier":
		output += "{0}\n{1}\n{2}".format(tree.leaf[2], tree.leaf[0], output_as_identifier(tree.leaf))
		# f.write(output)
	elif tree.type == "not" or tree.type == "isvoid":
		output += "{0}\n{1}\n".format(tree.leaf[2], tree.leaf[0])
		# f.write(output)
	elif tree.type == "tilde":
		output += "{0}\n{1}\n".format(tree.leaf[2], "negate")
		# f.write(output)
	elif tree.type in ["plus", "minus", "times", "divide", "lt", "le"]:
		output += "{0}\n{1}\n".format(tree.leaf[2], tree.leaf[0])
	elif tree.type == "equals":
		output += "{0}\n{1}\n".format(tree.leaf[2], "eq")
	elif tree.type == "new":
		output += "{0}\n{1}\n{2}".format(tree.leaf[0][2], tree.leaf[0][0], output_as_identifier(tree.leaf[1]))
	elif tree.type == "block":
		output += "{0}\n{1}\n".format(tree.leaf[2], "block")
		output += "{0}\n".format(len(tree.children))
	elif tree.type == "while":
		output += "{0}\nwhile\n".format(tree.leaf[2])
	elif tree.type == "if":
		output += "{0}\nif\n".format(tree.leaf[2])
	elif tree.type == "assign":
		output += "{0}\nassign\n{1}".format(tree.leaf[2], output_as_identifier(tree.leaf))
	elif tree.type == "static_dispatch":
		output += "{0}\nstatic_dispatch\n".format(tree.leaf["lineno"])
		recurse_tree(tree.leaf["expression"])
		output += "{0}{1}".format(output_as_identifier(tree.leaf["type"]), output_as_identifier(tree.leaf["method"]))
		output += "{0}\n".format(len(tree.children))
	elif tree.type == "dynamic_dispatch":
		output += "{0}\ndynamic_dispatch\n".format(tree.leaf["lineno"])
		recurse_tree(tree.leaf["expression"])
		output += output_as_identifier(tree.leaf["method"])
		output += "{0}\n".format(len(tree.children))
	elif tree.type == "self_dispatch":
		output += "{0}\nself_dispatch\n{1}".format(tree.leaf[2], output_as_identifier(tree.leaf))
		output += "{0}\n".format(len(tree.children))
	elif tree.type == "let_statement":
		output += "{0}\nlet\n{1}\n".format(tree.leaf["let"][2], len(tree.leaf["bindings"]))
		for elem in tree.leaf["bindings"]:
			recurse_tree(elem)
	elif tree.type == "let_binding_no_init":
		output += "let_binding_no_init\n{0}{1}".format(output_as_identifier(tree.leaf["identifier"]),
														output_as_identifier(tree.leaf["type"]))
	elif tree.type == "let_binding_init":
		output += "let_binding_init\n{0}{1}".format(output_as_identifier(tree.leaf["identifier"]),
													output_as_identifier(tree.leaf["type"]))
	elif tree.type == "case":
		output += "{0}\ncase\n".format(tree.leaf[0][2])
		recurse_tree(tree.leaf[1])
		output += "{0}\n".format(len(tree.children))
	elif tree.type == "case_element":
		output += "{0}{1}".format(output_as_identifier(tree.leaf[0]), output_as_identifier(tree.leaf[1]))
	elif tree.type == "parens":
		pass
	if not tree.children:
		return
	for elem in tree.children:
		recurse_tree(elem)

def output_ast(tree, fname):
	global output
	if os.path.exists(fname):
		os.remove(fname)
	recurse_tree(tree)
	with open(fname, "a+b") as f:
		f.write(output)

# Error rule for syntax errors
def p_error(p):
	if p is None:
		pass
	else:
		print "ERROR: {0}: Syntax Error".format(p.line_no)
		exit()

def read_tokens_create_lexer(filename):
	if os.path.exists(filename):
		three_liners = ("type", "identifier", "string", "integer")

		# Open the cl-lex file and read all lines
		with open(lex_fname, 'r+') as f:
			contents = f.readlines()

		index = 0
		lexer_instance = Lexer()
		while index < len(contents):
			# Read in the lexing tokens and add to Lexer
			line_no = contents[index].rstrip()
			token_type = contents[index+1].rstrip()
			value = None
			if token_type in three_liners:
				value = contents[index+2].rstrip()
				index += 3
			else:
				index += 2
			lexer_instance.add_token(token_type, line_no, value)
		return lexer_instance


	else:
		print "File Does Not Exist."
		return None

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Please provide a .cl-lex file as the only argument."
	else:
		lex_fname = sys.argv[1]
		output_fname = lex_fname.split('.')[0]  
		output_fname += ".cl-ast"

		lexer_instance = read_tokens_create_lexer(lex_fname)
		tokens = lexer_instance.token_types

		# Build the parser
		parser = yacc.yacc()
		# print parser.productions

		while True:
			result = parser.parse(lexer = lexer_instance)
			output_ast(result, output_fname)
			break
